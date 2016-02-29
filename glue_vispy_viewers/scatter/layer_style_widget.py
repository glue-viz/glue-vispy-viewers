from __future__ import absolute_import, division, print_function

import os

import numpy as np
from matplotlib import cm

from glue.core.subset import Subset
from glue.external.qt import QtGui

from glue.utils.qt import load_ui, update_combobox, connect_color
from glue.utils.qt.widget_properties import (ValueProperty,
                                             CurrentComboProperty,
                                             FloatLineProperty,
                                             connect_float_edit,
                                             connect_current_combo,
                                             connect_value)
from glue.viewers.common.qt.attribute_limits_helper import AttributeLimitsHelper


class ScatterLayerStyleWidget(QtGui.QWidget):

    # Size-related GUI elements
    size_attribute = CurrentComboProperty('ui.combo_size_attribute')
    size_vmin = FloatLineProperty('ui.value_size_vmin')
    size_vmax = FloatLineProperty('ui.value_size_vmax')
    size = FloatLineProperty('ui.value_fixed_size')
    size_scaling = ValueProperty('ui.slider_size_scaling')

    # Color-related GUI elements
    cmap_attribute = CurrentComboProperty('ui.combo_cmap_attribute')
    cmap_vmin = FloatLineProperty('ui.value_cmap_vmin')
    cmap_vmax = FloatLineProperty('ui.value_cmap_vmax')
    cmap = CurrentComboProperty('ui.combo_cmap')
    alpha = ValueProperty('ui.slider_alpha')

    def __init__(self, layer_artist):

        super(ScatterLayerStyleWidget, self).__init__()

        # Load ui file
        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        # Set up helpers to connect widgets

        self.size_limits = AttributeLimitsHelper(attribute_combo=self.ui.combo_size_attribute,
                                                 lower_value=self.ui.value_size_vmin,
                                                 upper_value=self.ui.value_size_vmax,
                                                 flip_button=self.ui.button_flip_size,
                                                 mode_combo=self.ui.combo_size_scale_mode)

        self.cmap_limits = AttributeLimitsHelper(attribute_combo=self.ui.combo_cmap_attribute,
                                                 lower_value=self.ui.value_cmap_vmin,
                                                 upper_value=self.ui.value_cmap_vmax,
                                                 flip_button=self.ui.button_flip_cmap,
                                                 mode_combo=self.ui.combo_cmap_scale_mode)

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # Set up size and color options
        self._setup_size_options()
        self._setup_color_options()
        self._connect_global()

        # Set initial values
        self.layer_artist.size = self.layer.style.markersize
        self.layer_artist.size_scaling = 1
        self.layer_artist.size_mode = 'fixed'
        self.ui.radio_size_fixed.setChecked(True)
        self.layer_artist.color = self.layer.style.color
        self.layer_artist.alpha = self.layer.style.alpha
        self.layer_artist.color_mode = 'fixed'
        self.ui.radio_color_fixed.setChecked(True)
        self.size_limits.data = self.layer
        self.cmap_limits.data = self.layer
        self.ui.combo_cmap.setCurrentIndex(0)
        self.layer_artist.visible = True

    def _connect_global(self):
        connect_float_edit(self.layer.style, 'markersize', self.ui.value_fixed_size)
        connect_color(self.layer.style, 'color', self.ui.label_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

    def _disconnect_global(self):
        # FIXME: Requires the ability to disconnect connections
        pass

    def _setup_size_options(self):

        # Set up radio buttons for size mode selection
        self._radio_size = QtGui.QButtonGroup()
        self._radio_size.addButton(self.ui.radio_size_fixed)
        self._radio_size.addButton(self.ui.radio_size_linear)

        # Set up connections with layer artist
        connect_float_edit(self.layer_artist, 'size', self.ui.value_fixed_size)
        connect_current_combo(self.layer_artist, 'size_attribute', self.ui.combo_size_attribute)
        connect_float_edit(self.layer_artist, 'size_vmin', self.ui.value_size_vmin)
        connect_float_edit(self.layer_artist, 'size_vmax', self.ui.value_size_vmax)
        connect_value(self.layer_artist, 'size_scaling', self.ui.slider_size_scaling, value_range=(0.1, 10), log=True)

        # Set up internal connections
        self.ui.radio_size_fixed.toggled.connect(self._update_size_mode)
        self.ui.radio_size_linear.toggled.connect(self._update_size_mode)

    def _update_size_mode(self):
        if self.ui.radio_size_fixed.isChecked():
            self.layer_artist.size_mode = 'fixed'
        else:
            self.layer_artist.size_mode = 'linear'

    def _setup_color_options(self):

        # Set up radio buttons for color mode selection
        self._radio_color = QtGui.QButtonGroup()
        self._radio_color.addButton(self.ui.radio_color_fixed)
        self._radio_color.addButton(self.ui.radio_color_linear)

        # Set up connections with layer artist
        connect_color(self.layer_artist, 'color', self.ui.label_color)
        connect_current_combo(self.layer_artist, 'cmap_attribute', self.ui.combo_cmap_attribute)
        connect_float_edit(self.layer_artist, 'cmap_vmin', self.ui.value_cmap_vmin)
        connect_float_edit(self.layer_artist, 'cmap_vmax', self.ui.value_cmap_vmax)
        connect_current_combo(self.layer_artist, 'cmap', self.ui.combo_cmap)
        connect_value(self.layer_artist, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

        # Set up internal connections
        self.ui.radio_color_fixed.toggled.connect(self._update_color_mode)
        self.ui.radio_color_linear.toggled.connect(self._update_color_mode)

    def _update_color_mode(self):
        if self.ui.radio_color_fixed.isChecked():
            self.layer_artist.color_mode = 'fixed'
        else:
            self.layer_artist.color_mode = 'linear'
