import os
import six
import numpy as np
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
# from palettable.colorbrewer import COLOR_MAPS
from vispy.color import Colormap, get_colormaps
# from .mpl_widget import MplWidget, defer_draw


__all__ = ["VolumeOptionsWidget"]

# UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')
UI_MAIN = '/Users/penny/Works/glue-3d-viewer/vispy_volume/options_widget.ui'

class VolumeOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(VolumeOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            return
        for map_name in get_colormaps():
            self.ui.cmap_menu.addItem(map_name)

        # self.ui.apply.clicked.connect(self.update_viewer)

        self._vispy_widget = vispy_widget
        # self.levels = []
        # self.spectral_stretch = 1.
        # self.alpha = 0.5

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_live)
        # self.ui.alpha_slider.valueChanged.connect(self.update_live)
        # self.ui.values_field.returnPressed.connect(self.update_live)
        # self.ui.spectral_stretch_field.returnPressed.connect(self.update_live)

    def update_live(self):
        # if self.live:
        self.update_viewer()

    def update_viewer(self):
        # self._vispy_widget.spectral_stretch = self.spectral_stretch
        self._vispy_widget.opaque_cmap = self.cmap
        # self._vispy_widget.alpha = self.alpha
        # self._vispy_widget.levels = self.levels
        self._vispy_widget.translucent_cmap = self.cmap

    '''@defer_draw
    def _update_render_console(self, is_monochrome):
        if is_monochrome:
            self.ui.rgb_options.hide()
            self.ui.mono_att_label.show()
            self.ui.attributeComboBox.show()
            self.client.rgb_mode(False)
        else:
            self.ui.mono_att_label.hide()
            self.ui.attributeComboBox.hide()
            self.ui.rgb_options.show()
            rgb = self.client.rgb_mode(True)
            if rgb is not None:
                self.ui.rgb_options.artist = rgb'''

    '''@property
    def live(self):
        return self.ui.live_checkbox.isChecked()

    @property
    def spectral_stretch(self):
        return float(self.ui.spectral_stretch_field.text())

    @spectral_stretch.setter
    def spectral_stretch(self, spectral_stretch):
        self.ui.spectral_stretch_field.setText("{0:g}".format(spectral_stretch))

    @property
    def alpha(self):
        return self.ui.alpha_slider.value() / 100.

    @alpha.setter
    def alpha(self, value):
        return self.ui.alpha_slider.setValue(value * 100.)'''

    @property
    def cmap(self):
        return self.ui.cmap_menu.currentText()

    @cmap.setter
    def cmap(self, value):
        index = self.ui.cmap_menu.fingText(value)
        self.ui.cmap_menu.setCurrentIndex(index)

    '''@property
    def levels(self):
        text = self.ui.values_field.text()
        try:
            return np.array(text.split(','), dtype=float)
        except:
            QtGui.QMessageBox.critical(self,
                                       "Error", "Could not parse levels: {0}".format(text),
                                       buttons=QtGui.QMessageBox.Ok)
            return np.array([])

    @levels.setter
    def levels(self, levels):
        if isinstance(levels, six.string_types):
            self.ui.values_field.setText(levels)
        else:
            self.ui.values_field.setText(", ".join([str(x) for x in levels]))'''


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
