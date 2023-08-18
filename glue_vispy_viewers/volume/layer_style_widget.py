import os

from glue.core.subset import Subset

from qtpy import QtWidgets

from glue_qt.utils import load_ui
from echo.qt import autoconnect_callbacks_to_qt


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

        # autoconnect needs to come after setting up the component IDs
        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.))}
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)

        # Set up radio buttons for subset mode selection if this is a subset
        if isinstance(self.layer, Subset):
            self._radio_size = QtWidgets.QButtonGroup()
            self._radio_size.addButton(self.ui.radio_subset_outline)
            self._radio_size.addButton(self.ui.radio_subset_data)
            self.ui.radio_subset_outline.toggled.connect(self._update_subset_mode)
            self.ui.radio_subset_data.toggled.connect(self._update_subset_mode)
            self.ui.valuetext_vmin.hide()
            self.ui.valuetext_vmax.hide()
            self.ui.label_limits.hide()
        else:
            self.ui.radio_subset_outline.hide()
            self.ui.radio_subset_data.hide()
            self.ui.label_subset_mode.hide()

    def _update_subset_mode(self):
        if self.ui.radio_subset_outline.isChecked():
            self.state.subset_mode = 'outline'
        else:
            self.state.subset_mode = 'data'
