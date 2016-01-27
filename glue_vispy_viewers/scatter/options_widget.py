import os
import math

from glue.external.qt import QtGui

try:
    from glue.utils.qt.widget_properties import CurrentComboProperty, TextProperty, ValueProperty
except ImportError:
    from glue.qt.widget_properties import CurrentComboProperty, TextProperty, ValueProperty

from glue.qt.qtutil import load_ui

from vispy.color import get_color_names

__all__ = ["ScatOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')


class ScatOptionsWidget(QtGui.QWidget):

    cmin = TextProperty('ui.clim_min')
    cmax = TextProperty('ui.clim_max')

    color = CurrentComboProperty('ui.ColorComboBox')
    opacity = ValueProperty('ui.OpacitySlider')

    def __init__(self, parent=None, vispy_widget=None):

        super(ScatOptionsWidget, self).__init__(parent=parent)

        print('UI_Main', UI_MAIN)
        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            raise Exception("Unable to load UI file: {0}".format(UI_MAIN))

        self._event_lock = False

        self._vispy_widget = vispy_widget
        if vispy_widget is not None:
            self._vispy_widget.options_widget = self

        self.stretch_sliders = [self.ui.x_stretch_slider,
                                self.ui.y_stretch_slider,
                                self.ui.z_stretch_slider,
                                self.ui.size_stretch_slider]

        self.slider_values = [self.ui.x_val,
                              self.ui.y_val,
                              self.ui.z_val,
                              self.ui.size_val]

        for idx in range(4):
            self._update_labels_from_sliders(idx)

        # Constrain size of slider value boxes
        for slider_value in self.slider_values:
            slider_value.setMaximumWidth(60)
            slider_value.setFixedWidth(60)

        # There are 155 color options
        for map_name in get_color_names():
            self.ui.ColorComboBox.addItem(map_name, map_name)

        # Add a color display area here
        self.color_view = self.ui.graphicsView
        self.color_scene = QtGui.QGraphicsScene()
        self.color_view.setBackgroundBrush(QtGui.QColor(self.color))
        self.color_view.setScene(self.color_scene)
        self.color_view.show()

        self.true_color = self.color
        self._reset_clim()
        self._connect()

    def _connect(self):
        self.ui.axis_apply.clicked.connect(self._apply)
        self.ui.reset_button.clicked.connect(self._reset_view)
        self.ui.ClimComboBox.currentIndexChanged.connect(self._clim_combo_change)
        self.ui.ColorComboBox.currentIndexChanged.connect(self._color_change)
        self.ui.OpacitySlider.valueChanged.connect(self._refresh_viewer)

        self.ui.clim_min.returnPressed.connect(self._refresh_viewer)
        self.ui.clim_max.returnPressed.connect(self._refresh_viewer)
        self.ui.advanceButton.clicked.connect(self._color_picker_show)

        # Connect slider and values both ways
        from functools import partial
        for idx in range(4):
            self.stretch_sliders[idx].valueChanged.connect(partial(self._update_labels_from_sliders, idx))
            self.stretch_sliders[idx].valueChanged.connect(self._refresh_viewer)

            self.slider_values[idx].returnPressed.connect(partial(self._update_sliders_from_labels, idx))

    def set_valid_components(self, components):
        self.ui.xAxisComboBox.clear()
        self.ui.yAxisComboBox.clear()
        self.ui.zAxisComboBox.clear()
        self.ui.SizeComboBox.clear()
        self.ui.ClimComboBox.clear()
        for component in components:
            self.ui.xAxisComboBox.addItem(component, component)
            self.ui.yAxisComboBox.addItem(component, component)
            self.ui.zAxisComboBox.addItem(component, component)
            self.ui.SizeComboBox.addItem(component, component)
            self.ui.ClimComboBox.addItem(component, component)

    def _reset_clim(self):
        self.cmin = 'auto'
        self.cmax = 'auto'

    def _clim_combo_change(self):
        if self._vispy_widget is not None:
            self._vispy_widget._update_clim()

    def _apply_clim(self):
        if self._vispy_widget is not None:
            self._vispy_widget.apply_clim()

    def _apply(self):
        """
        Add or update basic properties to display a scatter visual
        """
        if self._vispy_widget.scat_visual is None:
            self._vispy_widget.add_scatter_visual()
        else:
            # Only axis & size combo refresh
            self._reset_clim()
            self._refresh_viewer()

    def _reset_view(self):
        """
        Reset sliders, camera, clim combobox & text
        """
        for idx in range(4):
            self.stretch_sliders[idx].setValue(0)
        self._reset_clim()

        if self._vispy_widget is not None:
            self._vispy_widget.view.camera.reset()
        self._refresh_viewer()

    def _color_picker_show(self):
        color = QtGui.QColorDialog.getColor()
        self.true_color = color.name()
        self.color_view.setScene(self.color_scene)
        self.color_view.setBackgroundBrush(QtGui.QColor(self.true_color))
        self.color_view.show()

    def _color_change(self):
        self.color_view.setScene(self.color_scene)
        self.color_view.setBackgroundBrush(QtGui.QColor(self.color))
        self.color_view.show()
        self.true_color = self.color

    def _opacity_change(self):
        if self._vispy_widget is not None:
            self._vispy_widget.opacity_change()

    def _refresh_viewer(self):
        # Including sliders update
        if self._vispy_widget is not None:
            self._vispy_widget._refresh()

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