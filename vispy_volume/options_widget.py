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
            return None
        for map_name in get_colormaps():
            self.ui.cmap_menu.addItem(map_name)

        # Set up default values for side panel
        self._vispy_widget = vispy_widget
        self._widget_data = None
        self._stretch_scale = [1, 1, 1]
        self._stretch_tran = []
        self._slider_value = {}
        self.cmap = 'grays'
        self.stretch_menu_item = 'RA'

        # Add an instruction for fly camera keypress
        _canvas = self._vispy_widget.canvas
        self.fly_text = scene.visuals.Text('', parent=_canvas.scene, color=[1, 1, 1, 0.7],
                                           bold=True, font_size=16, pos=[_canvas.size[0]/2, _canvas.size[1]/2])

        self.ui.label_2.hide()
        # UI control connect
        self.ui.ra_stretchSlider.valueChanged.connect(lambda: self.update_stretch_slider(which_slider=0))
        self.ui.dec_stretchSlider.valueChanged.connect(lambda: self.update_stretch_slider(which_slider=1))
        self.ui.vel_stretchSlider.valueChanged.connect(lambda: self.update_stretch_slider(which_slider=2))

        self.ui.nor_mode.toggled.connect(self._update_render_method)

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_viewer)
        self.ui.reset_button.clicked.connect(self.reset_camera)

    def reset_camera(self):
        self._vispy_widget.view.camera.reset()
        self.update_viewer()

        self._stretch_scale = [1, 1, 1]
        self._vispy_widget.vol_visual.transform.scale = self._stretch_scale
        self._vispy_widget.vol_visual.transform.translate = self._stretch_tran

    def update_stretch_slider(self, which_slider):
        _index = which_slider
        self._stretch_scale[_index] = self.stretch_value(_index)
        self._stretch_tran[_index] = -self.stretch_value(_index)*self._widget_data.shape[2-_index]/2
        self._vispy_widget.vol_visual.transform.translate = self._stretch_tran
        self._vispy_widget.vol_visual.transform.scale = self._stretch_scale

    def update_viewer(self):
        self._widget_data = self._vispy_widget.get_data()
        self._stretch_tran = [-self._widget_data.shape[2]/2, -self._widget_data.shape[1]/2, -self._widget_data.shape[0]/2]

        _cube_data = self._vispy_widget.get_data()
        _cube_dist = sqrt(_cube_data.shape[0]**2 + _cube_data.shape[1]**2 + _cube_data.shape[2]**2)
        self._vispy_widget.vol_visual.cmap = self.cmap

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
    def stretch_value(self, which_slider):
        if which_slider == 0:
            return 10.0**(self.ui.ra_stretchSlider.value()/10.0)
        elif which_slider == 1:
            return 10.0**(self.ui.dec_stretchSlider.value()/10.0)
        elif which_slider == 2:
            return 10.0**(self.ui.vel_stretchSlider.value()/10.0)
        else:
            return None

    def set_stretch_value(self, which_slider, value):
        if which_slider == 0:
            return self.ui.ra_stretchSlider.setValue(10.0**(value*10.0))
        elif which_slider == 1:
            return self.ui.dec_stretchSlider.setValue(10.0**(value*10.0))
        elif which_slider == 2:
            return self.ui.vel_stretchSlider.setValue(10.0**(value*10.0))
        else:
            return None

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
