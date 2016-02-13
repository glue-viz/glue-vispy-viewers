from __future__ import absolute_import, division, print_function

import os

from matplotlib.colors import colorConverter

from glue.external.qt import QtGui
from glue.utils.qt import load_ui, mpl_to_qt4_color, qt4_to_mpl_color, update_combobox
from glue.utils.qt.widget_properties import ValueProperty, CurrentComboProperty, FloatLineProperty, connect_value
from glue.external.echo import add_callback
from .colors import get_translucent_cmap


class VolumeLayerStyleWidget(QtGui.QWidget):

    attribute = CurrentComboProperty('ui.combo_attribute')
    vmin = FloatLineProperty('ui.value_min')
    vmax = FloatLineProperty('ui.value_max')
    alpha = ValueProperty('ui.slider_alpha')

    def __init__(self, layer_artist):

        super(VolumeLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self._setup_color_label()

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer
        self.set_color(mpl_to_qt4_color(self.layer.style.color))
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, scaling=1./100.)
        self.ui.value_min.returnPressed.connect(self._update_limits)
        self.ui.value_max.returnPressed.connect(self._update_limits)
        self.ui.combo_attribute.currentIndexChanged.connect(self._update_attribute)
        self.ui.slider_alpha.valueChanged.connect(self._update_alpha)
        add_callback(self.layer.style, 'color', self._update_color)

        self._limits = {}

        self._update_attributes()

    def _update_color(self, value):
        rgb = colorConverter.to_rgb(value)
        cmap = get_translucent_cmap(*rgb)
        self.layer_artist.set(cmap=cmap)

    def _update_attributes(self):
        labels = [(comp.label, comp) for comp in self.layer.visible_components]
        update_combobox(self.ui.combo_attribute, labels)
        self.ui.combo_attribute.setCurrentIndex(0)

    @property
    def _data(self):
        return self.layer[self.attribute.label]

    def _update_alpha(self):
        # TODO: add scaling to ValueProperty
        self.layer_artist.set_alpha(self.alpha / 100.)

    def _update_limits(self):
        self._limits[self.attribute.label] = self.vmin, self.vmax
        self.layer_artist.set(clim=(self.vmin, self.vmax))

    def _update_attribute(self):
        if self.attribute not in self._limits:
            data = self._data
            self._limits[self.attribute.label] = data.min(), data.max()
        self.vmin, self.vmax = self._limits[self.attribute.label]
        self.layer_artist.set(clim=(self.vmin, self.vmax), attribute=self.attribute.label)

    def _setup_color_label(self):
        self.label_color.mousePressed.connect(self.query_color)

    def query_color(self, *args):
        color = QtGui.QColorDialog.getColor(self._color, self.label_color)
        if color.isValid():
            self.set_color(color)

    def set_color(self, color):
        self._color = color

        im = QtGui.QImage(80, 20, QtGui.QImage.Format_RGB32)
        im.fill(color)
        pm = QtGui.QPixmap.fromImage(im)
        self.label_color.setPixmap(pm)
        self.layer.style.color = qt4_to_mpl_color(self._color)
