import os
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
from vispy.color import get_colormaps


__all__ = ["VolumeOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')
# UI_MAIN = '/Users/penny/Works/glue-3d-viewer/vispy_volume/options_widget.ui'

class VolumeOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(VolumeOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            return
        for map_name in get_colormaps():
            self.ui.cmap_menu.addItem(map_name)

        self._vispy_widget = vispy_widget

        self.ui.threshold_lab.hide()
        self.ui.threshold_slider.hide()

        # UI control connect
        self.ui.cmap_menu.currentIndexChanged.connect(self.update_viewer)
        self.ui.threshold_slider.valueChanged.connect(self.update_threshold)
        self.ui.vol_radio.toggled.connect(self._update_render_method)

    def update_threshold(self):
        self._vispy_widget.volume1.threshold = self.threshold

    def update_viewer(self):
        self._vispy_widget.volume1.cmap = self.cmap


    def _update_render_method(self, is_volren):
        if is_volren:
            self.ui.threshold_slider.hide()
            self.ui.threshold_lab.hide()
            self._vispy_widget.volume1.method = 'mip'

        else:
            self.ui.threshold_slider.show()
            self.ui.threshold_lab.show()
            self._vispy_widget.volume1.method = 'iso'

    @property
    def threshold(self):
        return self.ui.threshold_slider.value() / 100.

    @threshold.setter
    def threshold(self, value):
        return self.ui.threshold_slider.setValue(value * 100.)

    @property
    def cmap(self):
        return self.ui.cmap_menu.currentText()

    @cmap.setter
    def cmap(self, value):
        index = self.ui.cmap_menu.fingText(value)
        self.ui.cmap_menu.setCurrentIndex(index)


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
