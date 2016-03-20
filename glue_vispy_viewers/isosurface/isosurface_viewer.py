from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import IsosurfaceLayerArtist
from .layer_style_widget import IsosurfaceLayerStyleWidget
from .isosurface_toolbar import IsosurfaceSelectionToolbar


class VispyIsosurfaceViewer(BaseVispyViewer):

    LABEL = "3D Isosurface Rendering"

    _layer_style_widget_cls = IsosurfaceLayerStyleWidget
    _toolbar_cls = IsosurfaceSelectionToolbar

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        layer_artist = IsosurfaceLayerArtist(data, vispy_viewer=self._vispy_widget)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        return True

    def add_subset(self, subset):
        if subset in self._layer_artist_container:
            return

        if subset.to_mask().ndim != 3:
            return

        layer_artist = IsosurfaceLayerArtist(subset, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_attributes(self, index=None, layer_artist=None):
        pass
