from __future__ import absolute_import, division, print_function

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import ScatterLayerArtist
from .layer_style_widget import ScatterLayerStyleWidget
from .viewer_state import Vispy3DScatterViewerState

from ..common import tools as _tools, selection_tools  # noqa
from . import scatter_toolbar  # noqa


class VispyScatterViewer(BaseVispyViewer):

    LABEL = "3D Scatter"

    _state_cls = Vispy3DScatterViewerState
    _layer_style_widget_cls = ScatterLayerStyleWidget

    tools = BaseVispyViewer.tools + ['vispy:lasso', 'vispy:rectangle',
                                     'vispy:circle', 'scatter3d:point']

    _data_artist_cls = ScatterLayerArtist
    _subset_artist_cls = ScatterLayerArtist

    def add_data(self, data):

        first_layer_artist = len(self._layer_artist_container) == 0

        added = super(VispyScatterViewer, self).add_data(data)

        if added:
            if first_layer_artist:
                self.state.set_limits(*self._layer_artist_container[0].default_limits)
                self._ready_draw = True

        return added
