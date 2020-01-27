from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import IsosurfaceLayerArtist
from .layer_style_widget import IsosurfaceLayerStyleWidget
from .viewer_state import Vispy3DIsosurfaceViewerState

from ..common import tools as _tools, selection_tools  # noqa


class VispyIsosurfaceViewer(BaseVispyViewer):

    LABEL = "3D Isosurface Rendering"

    _state_cls = Vispy3DIsosurfaceViewerState
    _layer_style_widget_cls = IsosurfaceLayerStyleWidget

    tools = BaseVispyViewer.tools

    _data_artist_cls = IsosurfaceLayerArtist
    _subset_artist_cls = IsosurfaceLayerArtist

    def add_data(self, data):

        first_layer_artist = len(self._layer_artist_container) == 0

        added = super(VispyIsosurfaceViewer, self).add_data(data)

        if added:
            if first_layer_artist:
                self.state.set_limits(*self._layer_artist_container[0].bbox)
                self._ready_draw = True

        return added
