from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import ScatterLayerArtist
from .layer_style_widget import ScatterLayerStyleWidget


class VispyScatterViewer(BaseVispyViewer):

    LABEL = "3D Scatter Plot"

    _layer_style_widget_cls = ScatterLayerStyleWidget

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        first_layer_artist = len(self._layer_artist_container) == 0

        # TODO: check for categorical components here
        self._options_widget._update_attributes(data.visible_components)

        layer_artist = ScatterLayerArtist(data, vispy_viewer=self._vispy_widget)
        self._update_attributes(layer_artist)

        self._layer_artist_container.append(layer_artist)

        if first_layer_artist:
            self._options_widget.set_limits(*layer_artist.default_limits)

        return True

    def _add_subset(self, message):

        if message.subset in self._layer_artist_container:
            return

        layer_artist = ScatterLayerArtist(message.subset, vispy_viewer=self._vispy_widget)
        self._update_attributes(layer_artist)

        self._layer_artist_container.append(layer_artist)

    def _update_attributes(self, layer_artist=None):

        if layer_artist is None:
            layer_artists = self._layer_artist_container
        else:
            layer_artists = [layer_artist]

        for artist in layer_artists:
            artist.set_coordinates(self._options_widget.x_att,
                                   self._options_widget.y_att,
                                   self._options_widget.z_att)
