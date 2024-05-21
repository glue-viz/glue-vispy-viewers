import sys
import numpy as np

from glue.config import settings

from ..common.vispy_data_viewer import BaseVispyViewerMixin
from .layer_artist import VolumeLayerArtist
from .viewer_state import Vispy3DVolumeViewerState

from ..scatter.layer_artist import ScatterLayerArtist
from .volume_visual import MultiVolume

from ..common import tools as _tools, selection_tools  # noqa
from . import volume_toolbar  # noqa


class VispyVolumeViewerMixin(BaseVispyViewerMixin):

    LABEL = "3D Volume Rendering"

    _state_cls = Vispy3DVolumeViewerState

    tools = BaseVispyViewerMixin.tools + ['vispy:lasso', 'vispy:rectangle',
                                          'vispy:circle', 'volume3d:floodfill']

    def setup_widget_and_callbacks(self):

        super().setup_widget_and_callbacks()

        # We need to use MultiVolume instance to store volumes, but we should
        # only have one per canvas. Therefore, we store the MultiVolume
        # instance in the vispy viewer instance.

        # Set whether we are emulating a 3D texture. This needs to be
        # enabled as a workaround on Windows otherwise VisPy crashes.
        emulate_texture = (sys.platform == 'win32' and
                           sys.version_info[0] < 3)

        multivol = MultiVolume(emulate_texture=emulate_texture,
                               bgcolor=settings.BACKGROUND_COLOR)

        self._vispy_widget.add_data_visual(multivol)
        self._vispy_widget._multivol = multivol

        self.state.add_callback('resolution', self._update_resolution)
        self._update_resolution()

    def _update_clip(self, force=False):
        if hasattr(self._vispy_widget, '_multivol'):
            if (self.state.clip_data or force):
                dx = self.state.x_stretch * self.state.aspect[0]
                dy = self.state.y_stretch * self.state.aspect[1]
                dz = self.state.z_stretch * self.state.aspect[2]
                coords = np.array([[-dx, -dy, -dz], [dx, dy, dz]])
                coords = (self._vispy_widget._multivol.transform.imap(coords)[:, :3] /
                          self._vispy_widget._multivol.resolution)
                self._vispy_widget._multivol.set_clip(self.state.clip_data, coords.ravel())
            else:
                self._vispy_widget._multivol.set_clip(False, [0, 0, 0, 1, 1, 1])

    def _update_slice_transform(self):
        self._vispy_widget._multivol._update_slice_transform(self.state.x_min, self.state.x_max,
                                                             self.state.y_min, self.state.y_max,
                                                             self.state.z_min, self.state.z_max)

    def _update_resolution(self, *event):
        self._vispy_widget._multivol.set_resolution(self.state.resolution)
        self._update_slice_transform()
        self._update_clip()

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = ScatterLayerArtist
        else:
            cls = VolumeLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = ScatterLayerArtist
        else:
            cls = VolumeLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def add_data(self, data):

        first_layer_artist = len(self._layer_artist_container) == 0

        if data.ndim == 1:
            if first_layer_artist:
                raise Exception("Can only add a scatter plot overlay once "
                                "a volume is present")
        elif data.ndim == 3:
            if not self._has_free_volume_layers:
                self._warn_no_free_volume_layers()
                return False
        else:
            raise Exception("Data should be 1- or 3-dimensional ({0} dimensions "
                            "found)".format(data.ndim))

        added = super().add_data(data)

        if added:

            if data.ndim == 1:
                self._vispy_widget._update_limits()

            if first_layer_artist:
                # The above call to add_data may have added subset layers, some
                # of which may be incompatible with the data, so we need to now
                # explicitly use the layer for the actual data object.
                layer = self._layer_artist_container[data][0]
                self.state.set_limits(*layer.bbox)
                self._ready_draw = True
                self._update_slice_transform()

            self._show_free_layer_warning = True

        return added

    def add_subset(self, subset):

        if not self._has_free_volume_layers:
            self._warn_no_free_volume_layers()
            return False

        added = super().add_subset(subset)

        if added:
            self._show_free_layer_warning = True

        return added

    @property
    def _has_free_volume_layers(self):
        return (not hasattr(self._vispy_widget, '_multivol') or
                self._vispy_widget._multivol.has_free_slots)

    def _warn_no_free_volume_layers(self):
        if getattr(self, '_show_free_layer_warning', True):
            raise Exception("The volume viewer has reached the maximum number "
                            "of volume layers. To show more volume layers, remove "
                            "existing layers and try again.")

    def _update_appearance_from_settings(self, message):
        super()._update_appearance_from_settings(message)
        if hasattr(self._vispy_widget, '_multivol'):
            self._vispy_widget._multivol.set_background(settings.BACKGROUND_COLOR)

    def _toggle_clip(self, *args):
        if hasattr(self._vispy_widget, '_multivol'):
            self._update_clip()

    def __gluestate__(self, context):
        state = super().__gluestate__(context)
        state['_protocol'] = 2
        return state
