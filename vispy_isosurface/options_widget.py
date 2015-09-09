import os
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
from vispy.color import get_colormaps
from vispy import scene


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
        self._stretch_scale = [1, 1, 1]

        self.stretch_slider_value = 0
        self.cmap = 'hsl'
        self.stretch_menu_item = 'RA'

        # Add an instruction for fly camera keypress
        _canvas = self._vispy_widget.canvas
        self.fly_text = scene.visuals.Text('', parent=_canvas.scene, color=[1,1,1,0.7],\
                                      bold=True, font_size=16, pos=[_canvas.size[0]/2, _canvas.size[1]/2])
        # UI control connect
        self.ui.stretch_menu.currentIndexChanged.connect(self.update_stretch_menu)
        self.ui.stretch_slider.valueChanged.connect(self.update_stretch_slider)
        self.ui.nor_mode.toggled.connect(self._update_render_method)

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_viewer)
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
        self._vispy_widget.volume1.cmap = self.cmap
        self._vispy_widget.volume1.transform.scale = self._stretch_scale
        if self._vispy_widget.view.camera is self._vispy_widget.cam2:
            self._vispy_widget.cam2.distance = self._vispy_widget.get_vol().shape[1]

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


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
