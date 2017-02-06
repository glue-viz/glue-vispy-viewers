from __future__ import absolute_import, division, print_function

import os

from glue.core.subset import Subset

from qtpy import QtWidgets

from glue.utils.qt import load_ui
from glue.external.echo.qt import autoconnect_callbacks_to_qt
from glue.core.qt.data_combo_helper import ComponentIDComboHelper


class VolumeLayerStyleWidget(QtWidgets.QWidget):

    def __init__(self, layer_artist):

        super(VolumeLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.state = layer_artist.state

        if self.state.subset_mode == 'outline':
            self.ui.radio_subset_outline.setChecked(True)
        else:
            self.ui.radio_subset_data.setChecked(True)

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # TODO: the following (passing self.layer to data_collection as second argument)
        # is a hack and we need to figure out a better solution.
        self.att_helper = ComponentIDComboHelper(self.ui.combodata_attribute, self.layer)
        self.att_helper.append_data(self.layer)

        # autoconnect needs to come after setting up the component IDs
        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.))}
        autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)

        # Set up radio buttons for subset mode selection if this is a subset
        if isinstance(self.layer, Subset):
            self._radio_size = QtWidgets.QButtonGroup()
            self._radio_size.addButton(self.ui.radio_subset_outline)
            self._radio_size.addButton(self.ui.radio_subset_data)
            self.ui.radio_subset_outline.toggled.connect(self._update_subset_mode)
            self.ui.radio_subset_data.toggled.connect(self._update_subset_mode)
            self.ui.valuetext_vmin.setEnabled(False)
        else:
            self.ui.radio_subset_outline.hide()
            self.ui.radio_subset_data.hide()
            self.ui.label_subset_mode.hide()

    def _update_subset_mode(self):
        if self.ui.radio_subset_outline.isChecked():
            self.state.subset_mode = 'outline'
            self.ui.valuetext_vmin.hide()
            self.ui.valuetext_vmax.hide()
        else:
            self.state.subset_mode = 'data'
            self.ui.valuetext_vmin.show()
            self.ui.valuetext_vmax.show()
