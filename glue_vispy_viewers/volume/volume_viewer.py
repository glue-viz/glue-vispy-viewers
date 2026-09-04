import sys
import numpy as np

from glue.config import settings
from glue.viewers.common.viewer import Viewer
from vispy.scene.visuals import Line
from vispy.color import Color
from .viewer_state import (Vispy3DVolumeViewerState, cutting_plane_from_state,
                           cutting_plane_polygon)

from ..common.vispy_data_viewer import BaseVispyViewerMixin
from .layer_artist import VolumeLayerArtist

from ..scatter.layer_artist import ScatterLayerArtist
from .volume_visual import MultiVolume

from ..common import tools as _tools, selection_tools  # noqa
from . import volume_toolbar  # noqa


# Colour of the cutting-plane outline. 50% grey reads as roughly half the
# contrast of the foreground-coloured bounding box on either a black or a
# white background.
GRAY = (0.5, 0.5, 0.5)


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

        self.state.add_callback('x_att', self._update_slice_transform)
        self.state.add_callback('y_att', self._update_slice_transform)
        self.state.add_callback('z_att', self._update_slice_transform)
        self.state.add_callback('resolution', self._update_resolution)
        self._update_resolution()

        # Line visual outlining where the cutting plane meets the box.
        self._cut_outline = Line(pos=np.zeros((2, 3), dtype=np.float32),
                                 color=Color(GRAY),
                                 width=2, connect='strip')
        self._cut_outline.visible = False
        self._vispy_widget.add_data_visual(self._cut_outline)

        for attr in ('cut_enabled', 'cut_mode', 'cut_axis',
                     'cut_tilt', 'cut_rotation', 'cut_depth', 'cut_flip',
                     'resolution',
                     'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):
            self.state.add_callback(attr, self._update_cutting_plane)
        self.state.add_callback('cut_plane_image_opacity', self._update_cut_plane_image_opacity)
        self.state.add_callback('cut_plane_image_bgcolor', self._update_cut_plane_image_bgcolor)
        self._update_cutting_plane()
        self._update_cut_plane_image_opacity()

    def _update_cut_plane_image_opacity(self, *args):
        opacity = self.state.cut_plane_image_opacity if self.state.cut_enabled else 0.0
        self._vispy_widget._multivol.set_cut_plane_image_opacity(opacity)
        self._vispy_widget.canvas.update()

        # The volume texture is only re-sliced lazily (on att/resolution
        # changes), so flipping an axis limit would otherwise leave it stale
        # until the next camera move. Re-slice immediately when an axis
        # orientation flips so the cutting plane stays consistent right away.
        for attr in ('x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):
            self.state.add_callback(attr, self._resample_on_axis_flip)

    def _update_cut_plane_image_bgcolor(self, *args):
        self._vispy_widget._multivol.set_cut_plane_image_bgcolor(self.state.cut_plane_image_bgcolor)
        self._vispy_widget.canvas.update()

    def _resample_on_axis_flip(self, *args):
        bounds = self._vispy_widget._multivol._data_bounds
        if bounds is None:
            return
        # _data_bounds is ordered (z, y, x); compare each axis orientation
        # (sign of max - min) against the limits the texture was sampled with.
        (z_lo, z_hi, _), (y_lo, y_hi, _), (x_lo, x_hi, _) = bounds
        flipped = ((self.state.x_max - self.state.x_min) * (x_hi - x_lo) < 0 or
                   (self.state.y_max - self.state.y_min) * (y_hi - y_lo) < 0 or
                   (self.state.z_max - self.state.z_min) * (z_hi - z_lo) < 0)
        if flipped:
            self._update_slice_transform()

    def _update_cutting_plane(self, *args):
        plane = cutting_plane_from_state(self.state)
        self._vispy_widget._multivol.set_cutting_plane(plane)
        # cut_enabled gates the plane image as well, so re-push opacity when it toggles.
        self._update_cut_plane_image_opacity()
        polygon = cutting_plane_polygon(self.state)
        if polygon is None or len(polygon) < 3:
            self._cut_outline.visible = False
        else:
            # Close the polygon with connect='strip' by repeating the first vertex.
            closed = np.vstack([polygon, polygon[:1]]).astype(np.float32)
            self._cut_outline.set_data(pos=closed, color=Color(GRAY))
            self._cut_outline.visible = True
        self._vispy_widget.canvas.update()

    def _update_clip(self, force=False):
        if hasattr(self._vispy_widget, '_multivol'):
            if (self.state.clip_data or force):
                dx = self.state.x_stretch * self.state.aspect[0]
                dy = self.state.y_stretch * self.state.aspect[1]
                dz = self.state.z_stretch * self.state.aspect[2]
                coords = np.array([[-dx, -dy, -dz], [dx, dy, dz]])
                coords = (self._vispy_widget._multivol.transform.imap(coords)[:, :3] /
                          self._vispy_widget._multivol.resolution)
                # Flipping an axis limit (x_min > x_max) gives the transform a
                # negative scale, which swaps the two mapped corners so the clip
                # box comes out inverted (min > max) and the shader clips away
                # everything. Sort per-axis so the clip box stays well-formed.
                lo = np.minimum(coords[0], coords[1])
                hi = np.maximum(coords[0], coords[1])
                self._vispy_widget._multivol.set_clip(self.state.clip_data,
                                                      np.concatenate([lo, hi]))
            else:
                self._vispy_widget._multivol.set_clip(False, [0, 0, 0, 1, 1, 1])

    def _update_slice_transform(self, *args):
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
        elif data.ndim >= 3:
            if not self._has_free_volume_layers:
                self._warn_no_free_volume_layers()
                return False
        else:
            raise Exception("Data should be 1- or >3-dimensional ({0} dimensions "
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


class SimpleVispyVolumeViewer(VispyVolumeViewerMixin, Viewer):
    """
    A backend-independent 3D volume viewer.

    Same vispy rendering pipeline as the Qt and Jupyter viewers but without
    a UI framework. Useful for visual regression tests and scripted use of
    the rendering pipeline.
    """

    def __init__(self, session, state=None):
        super().__init__(session, state=state)
        self.setup_widget_and_callbacks()

    def close(self):
        # Volume rendering populates glue's PIXEL_CACHE / ARRAY_CACHE via the
        # fixed-resolution buffer; clearing layer artists releases those.
        self.cleanup()
