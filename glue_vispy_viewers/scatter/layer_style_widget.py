from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset
from matplotlib.colors import colorConverter

from glue import config
from glue.external.qt import QtGui
from glue.utils.qt import load_ui, mpl_to_qt4_color, qt4_to_mpl_color, update_combobox
from glue.utils.qt.widget_properties import ValueProperty, CurrentComboProperty, FloatLineProperty, connect_value
from glue.external.echo import add_callback


class ScatterLayerStyleWidget(QtGui.QWidget):

    # Size-related GUI elements
    size_attribute = CurrentComboProperty('ui.combo_size_attribute')
    size_vmin = FloatLineProperty('ui.value_size_vmin')
    size_vmax = FloatLineProperty('ui.value_size_vmax')
    size = FloatLineProperty('ui.value_size')
    size_scaling = ValueProperty('ui.slider_size_scaling')

    # Color-related GUI elements
    cmap_attribute = CurrentComboProperty('ui.combo_cmap_attribute')
    cmap_vmin = FloatLineProperty('ui.value_cmap_vmin')
    cmap_vmax = FloatLineProperty('ui.value_cmap_vmax')
    cmap = CurrentComboProperty('ui.combo_cmap')
    alpha = ValueProperty('ui.slider_alpha')

    def __init__(self, layer_artist):

        super(ScatterLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        self._setup_size_options()
        self._setup_color_options()

        self._limits = {}

        # Set up connections
        self.ui.slider_alpha.valueChanged.connect(self._update_alpha)
        add_callback(self.layer.style, 'color', self._update_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, scaling=1./100.)

        # Set initial values
        self._update_color(self.layer.style.color)
        self._update_alpha()
        self.layer_artist.visible = True

    def _setup_size_options(self):

        self._radio_size = QtGui.QButtonGroup()
        self._radio_size.addButton(self.ui.radio_size_fixed)
        self._radio_size.addButton(self.ui.radio_size_linear)

        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_size_attribute, label_data)

        self.ui.radio_size_fixed.setChecked(True)

        self.ui.radio_size_fixed.toggled.connect(self._update_fixed_size)

        self.ui.radio_size_linear.toggled.connect(self._update_linear_size)
        self.ui.combo_size_attribute.currentIndexChanged.connect(self._update_linear_size_combo)
        self.ui.value_size_vmin.returnPressed.connect(self._update_linear_size)
        self.ui.value_size_vmax.returnPressed.connect(self._update_linear_size)
        self.ui.slider_size_scaling.valueChanged.connect(self._update_linear_size)

        self._size_limits = {}

    def _setup_color_options(self):

        # For now, we disable colormap options for color
        self.ui.radio_color_linear.setEnabled(False)
        self.ui.combo_cmap_attribute.setEnabled(False)
        self.ui.value_cmap_vmin.setEnabled(False)
        self.ui.value_cmap_vmax.setEnabled(False)
        self.ui.combo_cmap.setEnabled(False)

        self._radio_color = QtGui.QButtonGroup()
        self._radio_color.addButton(self.ui.radio_color_fixed)
        self._radio_color.addButton(self.ui.radio_color_linear)

        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_size_attribute, label_data)

        self.ui.radio_color_fixed.setChecked(True)

        self.ui.radio_color_fixed.toggled.connect(self._update_color)

        self.ui.radio_color_linear.toggled.connect(self._update_linear_color)
        self.ui.combo_cmap_attribute.currentIndexChanged.connect(self._update_linear_color)
        self.ui.value_cmap_vmin.returnPressed.connect(self._update_linear_color)
        self.ui.value_cmap_vmax.returnPressed.connect(self._update_linear_color)
        self.ui.combo_cmap.currentIndexChanged.connect(self._update_linear_color)

        self._setup_color_label()

    def _setup_color_label(self):
        """
        Set up the label used to display the selected color
        """
        self.label_color.mousePressed.connect(self.query_color)

    def query_color(self, *args):
        color = QtGui.QColorDialog.getColor(self._current_qcolor, self.label_color)
        if color.isValid():
            # The following should trigger the calling of _update_color,
            # so we don't need to call it explicitly
            self.layer.style.color = qt4_to_mpl_color(color)

    def _update_fixed_size(self):
        self.layer_artist.set_size(size=self.size)

    def _update_linear_size_combo(self):
        if self.size_attribute in self._size_limits:
            self.size_vmin, self.size_vmax = self._size_limits[self.size_attribute]
        else:
            self.size_vmin = np.nanmin(self.layer[self.size_attribute])
            self.size_vmax = np.nanmax(self.layer[self.size_attribute])
            self._size_limits[self.size_attribute] = self.size_vmin, self.size_vmax

    def _update_linear_size(self):
        self.layer_artist.set_size(attribute=self.size_attribute,
                                    vmin=self.size_vmin, vmax=self.size_vmax,
                                    scaling=self.size_scaling / 200)

    def _update_linear_color(self):
        self.layer_artist.set_color(attribute=self.cmap_attribute,
                                    vmin=self.cmap_vmin, vmax=self.cmap_vmax,
                                    cmap=self.cmap)

    def _update_color(self, value=None):

        # Update the color box
        qcolor = mpl_to_qt4_color(self.layer.style.color)
        im = QtGui.QImage(80, 20, QtGui.QImage.Format_RGB32)
        im.fill(qcolor)
        pm = QtGui.QPixmap.fromImage(im)
        self.label_color.setPixmap(pm)
        self._current_qcolor = qcolor

        # Update the colormap for the visualization
        rgb = colorConverter.to_rgb(self.layer.style.color)
        self.layer_artist.set_color(color=rgb)

    def _update_alpha(self):
        # TODO: add scaling to ValueProperty
        self.layer_artist.set_alpha(self.alpha / 100.)

    @property
    def visible_components(self):
        if isinstance(self.layer, Subset):
            return self.layer.data.visible_components
        else:
            return self.layer.visible_components
