import os
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
from vispy.color import get_colormaps
from vispy import scene
from math import *


__all__ = ["VolumeOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')


class VolumeOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(VolumeOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            return
        for map_name in get_colormaps():
            self.ui.cmap_menu.addItem(map_name)

        for vol_name in ['RA', 'DEC', 'VEL']:
            self.ui.stretch_menu.addItem(vol_name)

        # Set up default values for side panel
        self._vispy_widget = vispy_widget
        self._widget_data = None
        self._stretch_scale = [1, 1, 1]
        self._stretch_tran = []
        # self.stretch_slider_value = 0
        self.cmap = 'hsl'
        self.stretch_menu_item = 'RA'

        # Add an instruction for fly camera keypress
        _canvas = self._vispy_widget.canvas
        self.fly_text = scene.visuals.Text('', parent=_canvas.scene, color=[1, 1, 1, 0.7],
                                           bold=True, font_size=16, pos=[_canvas.size[0]/2, _canvas.size[1]/2])

        self.ui.label_2.hide()
        # UI control connect
        self.ui.stretch_menu.currentIndexChanged.connect(self.update_stretch_menu)
        self.ui.stretch_slider.valueChanged.connect(self.update_stretch_slider)
        self.ui.nor_mode.toggled.connect(self._update_render_method)

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_viewer)
        self.ui.reset_button.clicked.connect(self.reset_camera)

    def reset_camera(self):
        self._vispy_widget.view.camera.reset()
        self.update_stretch_menu()
        self.update_viewer()

    def update_stretch_menu(self):
        self.stretch_slider_value = 0.0
        self._stretch_scale = [1, 1, 1]
        self._stretch_tran = [-self._widget_data.shape[2]/2, -self._widget_data.shape[1]/2, -self._widget_data.shape[0]/2]
        self._vispy_widget.volume1.transform.scale = self._stretch_scale
        self._vispy_widget.volume1.transform.translate = self._stretch_tran

    def update_stretch_slider(self):
        _index = self.ui.stretch_menu.currentIndex()
        self._stretch_scale[_index] = self.stretch_slider_value
        self._stretch_tran[_index] = -self.stretch_slider_value*self._widget_data.shape[2-_index]/2

        # _new_axis_scale = self._vispy_widget.widget_axis_scale[_index] + self.stretch_slider_value
        # self._vispy_widget.axis.transform.scale = _new_axis_scale
        self._vispy_widget.volume1.transform.translate = self._stretch_tran
        self._vispy_widget.volume1.transform.scale = self._stretch_scale

    def update_viewer(self):
        self._widget_data = self._vispy_widget.get_data()
        self._stretch_tran = [-self._widget_data.shape[2]/2, -self._widget_data.shape[1]/2, -self._widget_data.shape[0]/2]

        _cube_data = self._vispy_widget.get_data()
        _cube_dist = sqrt(_cube_data.shape[0]**2 + _cube_data.shape[1]**2 + _cube_data.shape[2]**2)
        self._vispy_widget.volume1.cmap = self.cmap

        # Set the camera factors
        if self._vispy_widget.view.camera is self._vispy_widget.turntableCamera:
            _turntableCamera_fov = self._vispy_widget.turntableCamera.fov
            _cam_dist = _cube_dist / (tan(radians(_turntableCamera_fov)))
            self._vispy_widget.turntableCamera.distance = _cam_dist
            self._vispy_widget.turntableCamera.scale_factor = _cube_dist

    def _update_render_method(self, is_volren):
        if is_volren:
            self._vispy_widget.view.camera = self._vispy_widget.turntableCamera
            self.ui.label_2.hide()
            self.ui.label_3.show()
            self.fly_text.text = ''

        else:
            self._vispy_widget.view.camera = self._vispy_widget.flyCamera
            self.ui.label_2.show()
            self.ui.label_3.hide()

    # Value from -10 to 10
    @property
    def stretch_slider_value(self):
        return 10.0**(self.ui.stretch_slider.value()/10.0)

    @stretch_slider_value.setter
    def stretch_slider_value(self, value):
        return self.ui.stretch_slider.setValue(10.0**(value*10.0))

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


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
