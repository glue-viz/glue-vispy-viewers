from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset

from glue.external.echo import delay_callback
from glue.external.qt import QtGui
from glue.utils.qt import load_ui, update_combobox
from glue.utils.qt.widget_properties import (ValueProperty,
                                             CurrentComboProperty,
                                             FloatLineProperty, connect_value,
                                             connect_float_edit,
                                             connect_current_combo)

from .colors import get_translucent_cmap
from ..common.color_box import connect_color


class VolumeLayerStyleWidget(QtGui.QWidget):

    # GUI elements
    attribute = CurrentComboProperty('ui.combo_attribute')
    vmin = FloatLineProperty('ui.value_min')
    vmax = FloatLineProperty('ui.value_max')
    alpha = ValueProperty('ui.slider_alpha')

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
        self.layer_artist.visible = True

    def _connect_global(self):
        connect_color(self.layer.style, 'color', self.ui.label_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

    def _setup_options(self):
        """
        Set up the combo box with the list of attributes
        """

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
        self.ui.combo_attribute.currentIndexChanged.connect(self._update_limits)

    def _update_limits(self):

        if not hasattr(self, '_limits'):
            self._limits = {}

        if self.attribute in self._limits:
            self.vmin, self.vmax = self._limits[self.attribute]
        else:
            self.vmin, self.vmax = self.default_limits(self.attribute)
            self._limits[self.attribute] = self.vmin, self.vmax

    def default_limits(self, attribute):
        # For subsets, we want to compute the limits based on the full
        # dataset not just the subset.
        if isinstance(self.layer, Subset):
            return 0, 2
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
