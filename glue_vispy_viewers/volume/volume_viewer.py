from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget


class VispyVolumeViewer(BaseVispyViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = VolumeLayerStyleWidget

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        layer_artist = VolumeLayerArtist(data, vispy_viewer=self._vispy_widget)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        return True

    def _add_subset(self, message):

        if message.subset in self._layer_artist_container:
            return

        if message.subset.to_mask().ndim != 3:
            return

        layer_artist = VolumeLayerArtist(message.subset, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)
