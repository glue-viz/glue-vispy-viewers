from __future__ import absolute_import, division, print_function

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import IsosurfaceLayerArtist
from .layer_style_widget import IsosurfaceLayerStyleWidget


class VispyIsosurfaceViewer(BaseVispyViewer):

    LABEL = "3D Isosurface Rendering"

    _layer_style_widget_cls = IsosurfaceLayerStyleWidget

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        layer_artist = IsosurfaceLayerArtist(layer=data, vispy_viewer=self)

        if len(self._layer_artist_container) == 0:
            self.state.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        for subset in data.subsets:
            self.add_subset(subset)

        return True

    def add_subset(self, subset):
        if subset in self._layer_artist_container:
            return

        if subset.to_mask().ndim != 3:
            return

        layer_artist = IsosurfaceLayerArtist(layer=subset, vispy_viewer=self)
        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)
