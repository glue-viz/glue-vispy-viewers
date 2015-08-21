__author__ = 'penny'
import os

import six
import numpy as np
from glue.external.qt import QtGui
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp
from palettable.colorbrewer import COLOR_MAPS

__all__ = ["VolumeOptionsWidget"]

# IOError: [Errno 2] No such file or directory: '/usr/local/lib/python2.7/
# site-packages/glue/qt/ui/usr/local/lib/python2.7/site-packages/
# glue_3d_viewer-0.1.dev0-py2.7.egg/vispy_volume/options_widget.ui'
_dir = os.path.dirname(os.path.abspath(__file__))
UI_MAIN = os.path.join(_dir, 'options_widget.ui')
print 'dir, UI_Main', dir, UI_MAIN

class VolumeOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(VolumeOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui(UI_MAIN, self)

        for map_name in COLOR_MAPS['Diverging']:
            self.ui.cmap_menu.addItem(map_name)

        self.ui.apply.clicked.connect(self.update_viewer)

        self._vispy_widget = vispy_widget
        self.levels = []
        self.spectral_stretch = 1.
        self.alpha = 0.5

        self.ui.cmap_menu.currentIndexChanged.connect(self.update_live)
        self.ui.alpha_slider.valueChanged.connect(self.update_live)
        self.ui.values_field.returnPressed.connect(self.update_live)
        self.ui.spectral_stretch_field.returnPressed.connect(self.update_live)

    def update_live(self):
        if self.live:
            self.update_viewer()

    def update_viewer(self):
        self._vispy_widget.spectral_stretch = self.spectral_stretch
        self._vispy_widget.cmap = self.cmap
        self._vispy_widget.alpha = self.alpha
        self._vispy_widget.levels = self.levels
        self._vispy_widget.render()

    @property
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
        return self.ui.alpha_slider.setValue(value * 100.)

    @property
    def cmap(self):
        return self.ui.cmap_menu.currentText()

    @cmap.setter
    def cmap(self, value):
        index = self.ui.cmap_menu.fingText(value)
        self.ui.cmap_menu.setCurrentIndex(index)

    @property
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
            self.ui.values_field.setText(", ".join([str(x) for x in levels]))


if __name__ == "__main__":
    app = get_qapp()
    d = VolumeOptionsWidget()
    d.show()
    app.exec_()
    app.quit()
