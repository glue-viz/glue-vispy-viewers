from ..common.vispy_data_viewer import BaseVispyViewerMixin
from .layer_artist import ScatterLayerArtist
from .viewer_state import Vispy3DScatterViewerState

from ..common import tools as _tools, selection_tools  # noqa
from . import scatter_toolbar  # noqa


class VispyScatterViewerMixin(BaseVispyViewerMixin):

    LABEL = "3D Scatter"

    _state_cls = Vispy3DScatterViewerState

    tools = BaseVispyViewerMixin.tools + ['vispy:lasso', 'vispy:rectangle',
                                          'vispy:circle', 'scatter3d:point']

    _data_artist_cls = ScatterLayerArtist
    _subset_artist_cls = ScatterLayerArtist

    def add_data(self, data):

        first_layer_artist = len(self._layer_artist_container) == 0

        added = super().add_data(data)

        if added:
            if first_layer_artist:
                # The above call to add_data may have added subset layers, some
                # of which may be incompatible with the data, so we need to now
                # explicitly use the layer for the actual data object.
                layer = self._layer_artist_container[data][0]
                self.state.set_limits(*layer.default_limits)
                self._ready_draw = True

        return added
