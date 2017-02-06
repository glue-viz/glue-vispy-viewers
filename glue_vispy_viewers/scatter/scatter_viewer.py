from __future__ import absolute_import, division, print_function

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import ScatterLayerArtist
from .layer_style_widget import ScatterLayerStyleWidget

from ..common import selection_tools  # noqa
from . import scatter_toolbar  # noqa


class VispyScatterViewer(BaseVispyViewer):

    LABEL = "3D Scatter Plot"

    _layer_style_widget_cls = ScatterLayerStyleWidget

    tools = BaseVispyViewer.tools + ['vispy:lasso', 'vispy:rectangle',
                                     'vispy:circle', 'scatter3d:point']

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        first_layer_artist = len(self._layer_artist_container) == 0

        layer_artist = ScatterLayerArtist(layer=data, vispy_viewer=self)

        self._layer_artist_container.append(layer_artist)

        if first_layer_artist:
            self.state.set_limits(*layer_artist.default_limits)

        for subset in data.subsets:
            self.add_subset(subset)

        return True

    def add_subset(self, subset):

        if subset in self._layer_artist_container:
            return

        layer_artist = ScatterLayerArtist(layer=subset, vispy_viewer=self)

        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)
