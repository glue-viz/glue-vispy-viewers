import os
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
from vispy.color import get_colormaps, get_colormap
from vispy import color

__all__ = ["IsosurfaceOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')

class IsosurfaceOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(IsosurfaceOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            return
        for map_name in get_colormaps():
            self.ui.cmap_menu.addItem(map_name)

        for vol_name in ['RA', 'DEC', 'VEL']:
            self.ui.stretch_menu.addItem(vol_name)

        # Set up default values for side panel
        self._vispy_widget = vispy_widget
        self._stretch_scale = [1, 1, 1]

        self.threshold = 0
        self.stretch_slider_value = 0
        self.cmap = 'hsl'
        self.stretch_menu_item = 'RA'

        # UI control connect
        self.ui.stretch_menu.currentIndexChanged.connect(self.update_stretch_menu)
        self.ui.stretch_slider.valueChanged.connect(self.update_stretch_slider)

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_viewer)
        self.ui.threshold_slider.valueChanged.connect(self.update_viewer)
        self.ui.reset_button.clicked.connect(self.reset_camera)

    def reset_camera(self):
        self._vispy_widget.view.camera.reset()
        self.cmap = 'hsl'
        self._stretch_scale = [1, 1, 1]
        self.update_viewer()

    def update_stretch_menu(self):
        self.stretch_slider_value = 0
        self._stretch_scale = [1, 1, 1]
        self.update_viewer()

    def update_stretch_slider(self):
        _index = self.ui.stretch_menu.currentIndex()
        self._stretch_scale[_index] = self.stretch_slider_value+1
        # _new_axis_scale = self._vispy_widget.widget_axis_scale[_index] + self.stretch_slider_value
        # self._vispy_widget.axis.transform.scale = _new_axis_scale
        self.update_viewer()

    def update_viewer(self):
        self._vispy_widget.isoVisual1.transform.scale = self._stretch_scale
        if self._vispy_widget.view.camera is self._vispy_widget.cam2:
            self._vispy_widget.cam2.distance = self._vispy_widget.get_data().shape[1]
            self._vispy_widget.cam2.scale_factor = self._vispy_widget.get_data().shape[1]


        # TODO: a cmap for isosurface shoud be added, just do a trick here
        _iso_color = get_colormap(self.cmap).colors[0]
        _iso_color.alpha = 0.3
        self._vispy_widget.isoVisual1._color = color.Color(_iso_color)
        self._vispy_widget.isoVisual1.level = self.threshold
        self._vispy_widget.isoVisual1.transform.scale = self._stretch_scale

    def _update_render_method(self, is_volren):
        if is_volren:
            self._vispy_widget.view.camera = self._vispy_widget.cam2
            self.fly_text.text = ''

        else:
            self._vispy_widget.view.camera = self._vispy_widget.cam1
            # _text_string = 'Key WASD for moving, IJKL for roll'
            _text_string = '* WASD or arrow keys - move around * SPACE - brake * FC - move up-down * IJKL or mouse - look around'
            self.fly_text.text = _text_string


    @property
    def stretch_slider_value(self):
        return self.ui.stretch_slider.value() / 10.

    @stretch_slider_value.setter
    def stretch_slider_value(self, value):
        return self.ui.stretch_slider.setValue(value * 10. )

    @property
    def stretch_menu_item(self):
        return self.ui.stretch_menu.currentText()

    @stretch_menu_item.setter
    def stretch_menu_item(self, value):
        index = self.ui.stretch_menu.findText(value)
        self.ui.stretch_menu.setCurrentIndex(index)

    @property
    def cmap(self):
        return self.ui.cmap_menu.currentText()

    @cmap.setter
    def cmap(self, value):
        index = self.ui.cmap_menu.findText(value)
        self.ui.cmap_menu.setCurrentIndex(index)

    @property
    def threshold(self):
        return self.ui.threshold_slider.value() / 20.     # The value limitation is 0~99

    @threshold.setter
    def threshold(self, value):
        return self.ui.threshold_slider.setValue(value * 20.)

if __name__ == "__main__":
    app = get_qapp()
    d = IsosurfaceOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
