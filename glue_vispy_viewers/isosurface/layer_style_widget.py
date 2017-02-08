from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset

from qtpy import QtWidgets

from glue.utils.qt import load_ui
from glue.external.echo.qt import autoconnect_callbacks_to_qt
from glue.core.qt.data_combo_helper import ComponentIDComboHelper


class IsosurfaceLayerStyleWidget(QtWidgets.QWidget):

    def __init__(self, layer_artist):

        super(IsosurfaceLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.state = layer_artist.state

        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.))}
        autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # TODO: the following (passing self.layer to data_collection as second argument)
        # is a hack and we need to figure out a better solution.
        self.att_helper = ComponentIDComboHelper(self.ui.combodata_attribute, self.layer)
        self.att_helper.append_data(self.layer)

        # Set up internal connections
        self.ui.combodata_attribute.currentIndexChanged.connect(self._update_levels)

    def _update_levels(self):

        if isinstance(self.layer, Subset):
            self.level = 0.5
            return

        if not hasattr(self, '_levels'):
            self._levels = {}

        if self.attribute in self._levels:
            self.level = self._levels[self.state.attribute]
        else:
            self.level = self.default_levels(self.state.attribute)
            self._levels[self.attribute] = self.level

    def default_levels(self, attribute):
        # For subsets, we want to compute the levels based on the full
        # dataset not just the subset.
        if isinstance(self.layer, Subset):
            return 0.5
        else:
            return np.nanmedian(self.layer[attribute])
