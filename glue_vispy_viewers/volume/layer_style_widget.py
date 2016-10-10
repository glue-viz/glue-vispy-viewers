from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset

from qtpy import QtWidgets

from glue.external.echo import delay_callback
from glue.utils.qt import load_ui, update_combobox, connect_color
from glue.utils.qt.widget_properties import (ButtonProperty,
                                             ValueProperty,
                                             CurrentComboProperty,
                                             FloatLineProperty, connect_value,
                                             connect_float_edit,
                                             connect_current_combo)


class VolumeLayerStyleWidget(QtWidgets.QWidget):

    # GUI elements
    attribute = CurrentComboProperty('ui.combo_attribute')
    vmin = FloatLineProperty('ui.value_min')
    vmax = FloatLineProperty('ui.value_max')
    alpha = ValueProperty('ui.slider_alpha', value_range=(0, 1))
    subset_outline = ButtonProperty('ui.radio_subset_outline')
    subset_data = ButtonProperty('ui.radio_subset_data')

    def __init__(self, layer_artist):

        super(VolumeLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # Set up attribute and visual options
        self._setup_options()
        self._connect_global()

        # Set initial values
        self.layer_artist.color = self.layer.style.color
        self.layer_artist.alpha = self.layer.style.alpha
        with delay_callback(self.layer_artist, 'attribute'):
            self.attribute = self.visible_components[0]
            self._update_limits()
        if isinstance(self.layer, Subset):
            self.ui.radio_subset_data.setChecked(True)
        self.layer_artist.visible = True

    def _connect_global(self):
        connect_color(self.layer.style, 'color', self.ui.label_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

    def _setup_options(self):
        """
        Set up the combo box with the list of attributes
        """

        # Set up radio buttons for subset mode selection if this is a subset
        if isinstance(self.layer, Subset):
            self._radio_size = QtWidgets.QButtonGroup()
            self._radio_size.addButton(self.ui.radio_subset_outline)
            self._radio_size.addButton(self.ui.radio_subset_data)
        else:
            self.ui.radio_subset_outline.hide()
            self.ui.radio_subset_data.hide()
            self.ui.label_subset_mode.hide()

        # Set up attribute list
        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_attribute, label_data)

        # Set up connections with layer artist
        connect_current_combo(self.layer_artist, 'attribute', self.ui.combo_attribute)
        connect_float_edit(self.layer_artist, 'vmin', self.ui.value_min)
        connect_float_edit(self.layer_artist, 'vmax', self.ui.value_max)
        connect_color(self.layer_artist, 'color', self.ui.label_color)
        connect_value(self.layer_artist, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

        # Set up internal connections
        self.ui.radio_subset_outline.toggled.connect(self._update_subset_mode)
        self.ui.radio_subset_data.toggled.connect(self._update_subset_mode)
        self.ui.value_min.editingFinished.connect(self._cache_limits)
        self.ui.value_max.editingFinished.connect(self._cache_limits)
        self.ui.combo_attribute.currentIndexChanged.connect(self._update_limits)

    def _update_subset_mode(self):
        if self.ui.radio_subset_outline.isChecked():
            self.layer_artist.subset_mode = 'outline'
        else:
            self.layer_artist.subset_mode = 'data'
        self._update_limits()

    def _update_limits(self):

        if isinstance(self.layer, Subset):
            if self.layer_artist.subset_mode == 'outline':
                self.ui.value_min.setEnabled(False)
                self.ui.value_max.setEnabled(False)
                self.vmin, self.vmax = 0, 2
                return
            else:
                self.ui.value_min.setEnabled(False)
                self.ui.value_max.setEnabled(True)

        if not hasattr(self, '_limits'):
            self._limits = {}

        if self.attribute in self._limits:
            self.vmin, self.vmax = self._limits[self.attribute]
        else:
            self.vmin, self.vmax = self.default_limits(self.attribute)
            self._limits[self.attribute] = self.vmin, self.vmax

    def _cache_limits(self):
        if not isinstance(self.layer, Subset) or self.layer_artist.subset_mode == 'data':
            self._limits[self.attribute] = self.vmin, self.vmax

    def default_limits(self, attribute):
        # For subsets, we want to compute the limits based on the full
        # dataset not just the subset.
        if isinstance(self.layer, Subset):
            vmin = 0
            vmax = np.nanmax(self.layer.data[attribute])
        else:
            vmin = np.nanmin(self.layer[attribute])
            vmax = np.nanmax(self.layer[attribute])
        return vmin, vmax

    @property
    def visible_components(self):
        if isinstance(self.layer, Subset):
            return self.layer.data.visible_components
        else:
            return self.layer.visible_components
