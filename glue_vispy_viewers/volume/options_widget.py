import os
import math

from glue.external.qt import QtGui
from glue.qt.widget_properties import CurrentComboProperty, WidgetProperty, TextProperty
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp

from vispy.color import get_colormaps

__all__ = ["VolumeOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')

# The following should go into the glue core package

class CurrentTabProperty(WidgetProperty):

    def getter(self, widget):
        """ Return the itemData stored in the currently-selected item """
        return widget.tabText(widget.currentIndex())

    def setter(self, widget, value):
        """ Update the currently selected item to the one which stores value in
        its itemData
        """
        for idx in range(widget.count()):
            if widget.tabText(idx) == value:
                break
        else:
            raise ValueError("%s not found in tabs" % value)

        widget.setCurrentIndex(idx)


# Need a slider property with custom mapping function


class VolumeOptionsWidget(QtGui.QWidget):

    visible_component = CurrentComboProperty('ui.component',
                                             'Visible component')

    view_mode = CurrentTabProperty('ui.view_tabs',
                                   'View mode')

    cmap = CurrentComboProperty('ui.cmap_menu',
                                'Colormap')

    slider_x_label = TextProperty('ui.x_val', 'x slider label')
    slider_y_label = TextProperty('ui.y_val', 'y slider label')
    slider_z_label = TextProperty('ui.z_val', 'z slider label')

    cmin = TextProperty('ui.clim_min')
    cmax = TextProperty('ui.clim_max')

    def __init__(self, parent=None, vispy_widget=None):

        super(VolumeOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            raise Exception("Unable to load UI file: {0}".format(UI_MAIN))

        self._event_lock = False

        for map_name in sorted(get_colormaps()):
            self.ui.cmap_menu.addItem(map_name, map_name)

        self._vispy_widget = vispy_widget
        if vispy_widget is not None:
            self._vispy_widget.options_widget = self

        self.stretch_sliders = [self.ui.x_stretch_slider,
                                self.ui.y_stretch_slider,
                                self.ui.z_stretch_slider]

        self.axis_labels = [self.ui.x_lab,
                            self.ui.y_lab,
                            self.ui.z_lab]

        self.slider_values = [self.ui.x_val,
                              self.ui.y_val,
                              self.ui.z_val]

        self._reset_clim()

        self._reset_view()

        for idx in range(3):
            self._update_labels_from_sliders(idx)

        # Constrain size of slider value boxes

        for slider_value in self.slider_values:
            slider_value.setMaximumWidth(60)
            slider_value.setFixedWidth(60)

        # Connect slider and values both wways
        from functools import partial
        for idx in range(3):

            self.stretch_sliders[idx].valueChanged.connect(partial(self._update_labels_from_sliders, idx))
            self.stretch_sliders[idx].valueChanged.connect(self._refresh_viewer)

            self.slider_values[idx].returnPressed.connect(partial(self._update_sliders_from_labels, idx))

        self.ui.component.currentIndexChanged.connect(self._reset_clim)

        self.ui.reset_button.clicked.connect(self._reset_view)
        self.ui.view_tabs.currentChanged.connect(self._refresh_viewer)
        self.ui.cmap_menu.currentIndexChanged.connect(self._refresh_viewer)
        self.ui.component.currentIndexChanged.connect(self._refresh_viewer)
        self.ui.clim_min.returnPressed.connect(self._refresh_viewer)
        self.ui.clim_max.returnPressed.connect(self._refresh_viewer)

    def set_valid_components(self, components):
        self.ui.component.clear()
        for component in components:
            self.ui.component.addItem(component, component)

    def set_axis_names(self, names):
        for idx in range(3):
            self.axis_labels[idx].setText(names[idx])

    def _reset_view(self):
        """
        Reset the sliders, colormap, view mode, and camera
        """

        for idx in range(3):
            self.stretch_sliders[idx].setValue(0)

        self.cmap = 'grays'

        self._reset_clim()

        self.view_mode = "Normal View Mode"

        if self._vispy_widget is not None:
            self._vispy_widget.view.camera.reset()

        self._refresh_viewer()

    def _reset_clim(self):
        self.cmin = 'auto'
        self.cmax = 'auto'

    @property
    def stretch(self):
        return [10.0 ** (slider.value()/1e4) for slider in self.stretch_sliders]

    def _update_labels_from_sliders(self, idx):
        if self._event_lock:
            return  # prevent infinite event loop
        self._event_lock = True
        try:
            self.slider_values[idx].setText("{0:6.2f}".format(self.stretch[idx]))
        finally:
            self._event_lock = False

    def _update_sliders_from_labels(self, idx):
        if self._event_lock:
            return  # prevent infinite event loop
        self._event_lock = True
        try:
            self.stretch_sliders[idx].setValue(1e4 * math.log10(float(self.slider_values[idx].text())))
        finally:
            self._event_lock = False

    def _refresh_viewer(self):
        if self._vispy_widget is not None:
            self._vispy_widget._refresh()


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
