import sys
import numpy as np

from glue.config import settings

from qtpy.QtWidgets import QMessageBox
from qtpy.QtCore import QTimer

from glue.core.data import BaseData
from glue.core.link_helpers import LinkSame

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget
from .viewer_state import Vispy3DVolumeViewerState
from .layer_state import VolumeLayerState
from .volume_visual import MultiVolume

from ..scatter.layer_artist import ScatterLayerArtist
from ..scatter.layer_style_widget import ScatterLayerStyleWidget

from ..common import tools as _tools, selection_tools  # noqa
from . import volume_toolbar  # noqa


class VispyVolumeViewer(BaseVispyViewer):

    LABEL = "3D Volume Rendering"

    _state_cls = Vispy3DVolumeViewerState
    _layer_style_widget_cls = {VolumeLayerArtist: VolumeLayerStyleWidget,
                               ScatterLayerArtist: ScatterLayerStyleWidget}

    tools = BaseVispyViewer.tools + ['vispy:lasso', 'vispy:rectangle',
                                     'vispy:circle', 'volume3d:floodfill']

    def __init__(self, *args, **kwargs):

        super(VispyVolumeViewer, self).__init__(*args, **kwargs)

        # We now make it so that is the user clicks to drag or uses the
        # mouse wheel (or scroll on a trackpad), we downsample the volume
        # rendering temporarily.

        canvas = self._vispy_widget.canvas

        canvas.events.mouse_press.connect(self.mouse_press)
        canvas.events.mouse_wheel.connect(self.mouse_wheel)
        canvas.events.mouse_release.connect(self.mouse_release)

        viewbox = self._vispy_widget.view.camera.viewbox

        viewbox.events.mouse_wheel.connect(self.camera_mouse_wheel)
        viewbox.events.mouse_move.connect(self.camera_mouse_move)
        viewbox.events.mouse_press.connect(self.camera_mouse_press)
        viewbox.events.mouse_release.connect(self.camera_mouse_release)

        self._downsampled = False

        # For the mouse wheel, we receive discrete events so we need to have
        # a buffer (for now 250ms) before which we consider the mouse wheel
        # event to have stopped.

        self._downsample_timer = QTimer()
        self._downsample_timer.setInterval(250)
        self._downsample_timer.setSingleShot(True)
        self._downsample_timer.timeout.connect(self.mouse_release)

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

        # We do this here in addition to in the volume viewer itself as for
        # some situations e.g. reloading from session files, a clip_data event
        # isn't emitted.
        # FIXME: needs to be done after first layer added
        # self._update_clip(force=True)

    def mouse_press(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol') and not self._downsampled:
                self._vispy_widget._multivol.downsample()
                self._downsampled = True

    def mouse_release(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol') and self._downsampled:
                self._vispy_widget._multivol.upsample()
                self._downsampled = False
                self._vispy_widget.canvas.render()

        self._update_slice_transform()
        self._update_clip()

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

    def mouse_wheel(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol'):
                if not self._downsampled:
                    self.mouse_press()
        self._downsample_timer.start()
        if event is not None:
            event.handled = True

    def resizeEvent(self, event=None):
        self.mouse_wheel()
        super(VispyVolumeViewer, self).resizeEvent(event)

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
                QMessageBox.critical(self, "Error",
                                     "Can only add a scatter plot overlay once "
                                     "a volume is present",
                                     buttons=QMessageBox.Ok)
                return False
        elif data.ndim == 3:
            if not self._has_free_volume_layers:
                self._warn_no_free_volume_layers()
                return False
        else:
            QMessageBox.critical(self, "Error",
                                 "Data should be 1- or 3-dimensional ({0} dimensions "
                                 "found)".format(data.ndim),
                                 buttons=QMessageBox.Ok)
            return False

        added = super(VispyVolumeViewer, self).add_data(data)

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

        added = super(VispyVolumeViewer, self).add_subset(subset)

        if added:
            self._show_free_layer_warning = True

        return added

    @property
    def _has_free_volume_layers(self):
        return (not hasattr(self._vispy_widget, '_multivol') or
                self._vispy_widget._multivol.has_free_slots)

    def _warn_no_free_volume_layers(self):
        if getattr(self, '_show_free_layer_warning', True):
            QMessageBox.critical(self, "Error",
                                 "The volume viewer has reached the maximum number "
                                 "of volume layers. To show more volume layers, remove "
                                 "existing layers and try again. This error will not "
                                 "be shown again unless the limit is reached again in "
                                 "the future.",
                                 buttons=QMessageBox.Ok)
            self._show_free_layer_warning = False

    def _update_appearance_from_settings(self, message):
        super(VispyVolumeViewer, self)._update_appearance_from_settings(message)
        if hasattr(self._vispy_widget, '_multivol'):
            self._vispy_widget._multivol.set_background(settings.BACKGROUND_COLOR)

    def _toggle_clip(self, *args):
        if hasattr(self._vispy_widget, '_multivol'):
            self._update_clip()

    @classmethod
    def __setgluestate__(cls, rec, context):

        viewer = super(VispyVolumeViewer, cls).__setgluestate__(rec, context)

        if rec.get('_protocol', 0) < 2:

            # Find all data objects in layers (not subsets)
            layer_data = [layer.layer for layer in viewer.state.layers
                          if (isinstance(layer, VolumeLayerState) and
                              isinstance(layer.layer, BaseData))]

            if len(layer_data) > 1:
                reference = layer_data[0]
                for data in layer_data[1:]:
                    if data not in reference.pixel_aligned_data:
                        break
                else:
                    return viewer

            buttons = QMessageBox.Yes | QMessageBox.No
            message = ("The 3D volume rendering viewer now requires datasets to "
                       "be linked in order to be shown at the same time. Are you "
                       "happy for glue to automatically link your datasets by "
                       "pixel coordinates?")

            answer = QMessageBox.question(None, "Link data?", message,
                                          buttons=buttons,
                                          defaultButton=QMessageBox.Yes)

            if answer == QMessageBox.Yes:
                for data in layer_data[1:]:
                    if data not in reference.pixel_aligned_data:
                        for i in range(3):
                            link = LinkSame(reference.pixel_component_ids[i],
                                            data.pixel_component_ids[i])
                            viewer.session.data_collection.add_link(link)

        return viewer

    def __gluestate__(self, context):
        state = super(VispyVolumeViewer, self).__gluestate__(context)
        state['_protocol'] = 2
        return state
