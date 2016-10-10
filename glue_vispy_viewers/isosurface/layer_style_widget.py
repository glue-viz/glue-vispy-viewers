from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset

from glue.external.echo import delay_callback

from qtpy import QtWidgets

from glue.utils.qt import load_ui, update_combobox, connect_color
from glue.utils.qt.widget_properties import (ValueProperty,
                                             CurrentComboProperty,
                                             FloatLineProperty, connect_value,
                                             connect_float_edit,
                                             connect_current_combo)


class IsosurfaceLayerStyleWidget(QtWidgets.QWidget):

    # GUI elements
    # this are for layer_artist to callback
    attribute = CurrentComboProperty('ui.combo_attribute')
    level_low = FloatLineProperty('ui.limits_low')  # could get and set float value
    level_high = FloatLineProperty('ui.limits_high')
    # We don't have IntLineProperty?
    step = ValueProperty('ui.slider_step')  # TODO: set default value here?

    def __init__(self, layer_artist):

        super(IsosurfaceLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # Set up attribute and visual options
        self._setup_options()
        self._connect_global()

        # Set initial values
        self.layer_artist.color = self.layer.style.color
        # TODO: alpha is now automatically set, in the future each level could be one layer
        # and its color, transparency and visibility could be set from layer panel
        # self.layer_artist.alpha = self.layer.style.alpha

        with delay_callback(self.layer_artist, 'attribute'):
            self.attribute = self.visible_components[0]
            self._update_levels()
        self.layer_artist.visible = True

    # this is for connect to layer.style
    def _connect_global(self):
        connect_color(self.layer.style, 'color', self.ui.label_color)
        # connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

    def _setup_options(self):  # for initiate
        """
        Set up the combo box with the list of attributes
        """

        # Set up attribute list
        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_attribute, label_data)

        # Set up connections with layer artist
        connect_current_combo(self.layer_artist, 'attribute', self.ui.combo_attribute)
        connect_float_edit(self.layer_artist, 'level_low', self.ui.limits_low)
        connect_float_edit(self.layer_artist, 'level_high', self.ui.limits_high)
        connect_color(self.layer_artist, 'color', self.ui.label_color)
        connect_value(self.layer_artist, 'step', self.ui.slider_step)
        # connect_value(self.layer_artist, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

        # Set up internal connections
        self.ui.limits_low.editingFinished.connect(self._cache_levels)
        self.ui.limits_high.editingFinished.connect(self._cache_levels)
        self.ui.combo_attribute.currentIndexChanged.connect(self._update_levels)

    def _update_levels(self):

        if isinstance(self.layer, Subset):
            self.level_low, self.level_high = 0, 0.5
            return

        if not hasattr(self, '_levels'):
            self._levels = {}

        if self.attribute in self._levels:
            self.level_low, self.level_high = self._levels[self.attribute]
        else:
            self.level_low, self.level_high = self.default_levels(self.attribute)
            self._levels[self.attribute] = self.level_low, self.level_high
        print('in update levels', self.level_low, self.level_high)

    def _cache_levels(self):
        if not isinstance(self.layer, Subset) or self.layer_artist.subset_mode == 'data':
            self._levels[self.attribute] = self.level_low, self.level_high

    def default_levels(self, attribute):
        # For subsets, we want to compute the limits based on the full
        # dataset not just the subset.
        if isinstance(self.layer, Subset):
            lmin = 0
            lmax = np.nanmax(self.layer.data[attribute])
        else:
            lmin = np.nanmin(self.layer[attribute])
            lmax = np.nanmax(self.layer[attribute])
        return lmin, lmax

    @property
    def visible_components(self):
        if isinstance(self.layer, Subset):
            return self.layer.data.visible_components
        else:
            return self.layer.visible_components
