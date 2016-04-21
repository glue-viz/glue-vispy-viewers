from glue.external.qt.QtGui import QMessageBox

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget
from .volume_toolbar import VolumeSelectionToolbar


class VispyVolumeViewer(BaseVispyViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = VolumeLayerStyleWidget
    _toolbar_cls = VolumeSelectionToolbar

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        if data.ndim != 3:
            QMessageBox.critical(self, "Error",
                                 "Data should be 3-dimensional ({0} dimensions found)".format(data.ndim),
                                 buttons=QMessageBox.Ok)
            return False

        if len(self._layer_artist_container) > 0:
            required_shape = self._layer_artist_container[0].shape
            if data.shape != required_shape:
                QMessageBox.critical(self, "Error",
                                     "Shape of dataset ({0}) does not agree "
                                     "with shape of existing datasets in volume "
                                     "rendering ({1})".format(data.shape, required_shape),
                                     buttons=QMessageBox.Ok)
                return False

        layer_artist = VolumeLayerArtist(data, vispy_viewer=self._vispy_widget)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        return True

    def add_subset(self, subset):
        if subset in self._layer_artist_container:
            return

        if subset.to_mask().ndim != 3:
            return

        layer_artist = VolumeLayerArtist(subset, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_attributes(self, index=None, layer_artist=None):
        pass
