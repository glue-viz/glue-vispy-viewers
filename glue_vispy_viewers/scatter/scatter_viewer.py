from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import ScatterLayerArtist
from .layer_style_widget import ScatterLayerStyleWidget


class VispyScatterViewer(BaseVispyViewer):

    LABEL = "3D Scatter Plot"

    # _layer_style_widget_cls = ScatterLayerStyleWidget

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True
        
        first_layer_artist = len(self._layer_artist_container) == 0

        # TODO: check for categorical components here
        self._options_widget._update_attributes(data.visible_components)

        layer_artist = ScatterLayerArtist(data, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)

        self._update_attributes()

        if first_layer_artist:
            self._options_widget.set_limits(*layer_artist.default_limits)

        return True

    def _add_subset(self, message):

        if message.subset in self._layer_artist_container:
            return

        if message.subset.to_mask().ndim != 3:
            return

        layer_artist = ScatterLayerArtist(message.subset, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)

    def _update_attributes(self):

        for artist in self._layer_artist_container:
            print("HERE",artist)
            artist.set_coordinates(self._options_widget.x_att,
                                   self._options_widget.y_att,
                                   self._options_widget.z_att)
