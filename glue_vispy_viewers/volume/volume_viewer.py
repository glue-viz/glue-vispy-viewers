from __future__ import absolute_import, division, print_function

import numpy as np

from glue.config import settings

from qtpy.QtWidgets import QMessageBox
from qtpy.QtCore import QTimer

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget
from .viewer_state import Vispy3DVolumeViewerState

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

        self.state.add_callback('resolution', self._update_resolution)

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
        if event is not None:
            self._downsample_timer.start()
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
                                     "a volume is present".format(data.ndim),
                                     buttons=QMessageBox.Ok)
                return False
        elif data.ndim == 3:
            if not first_layer_artist:
                required_shape = self.layers[0].shape
                if data.shape != required_shape:
                    QMessageBox.critical(self, "Error",
                                         "Shape of dataset ({0}) does not agree "
                                         "with shape of existing datasets in volume "
                                         "rendering ({1})".format(data.shape, required_shape),
                                         buttons=QMessageBox.Ok)
                    return False
        else:
            QMessageBox.critical(self, "Error",
                                 "Data should be 1- or 3-dimensional ({0} dimensions "
                                 "found)".format(data.ndim),
                                 buttons=QMessageBox.Ok)
            return False

        added = super(VispyVolumeViewer, self).add_data(data)

        if data.ndim == 1:
            self._vispy_widget._update_limits()

        if added:
            if first_layer_artist:
                self.state.set_limits(*self._layer_artist_container[0].bbox)
                self._ready_draw = True
                self._update_slice_transform()

        return added

    def _update_appearance_from_settings(self, message):
        super(VispyVolumeViewer, self)._update_appearance_from_settings(message)
        if hasattr(self._vispy_widget, '_multivol'):
            self._vispy_widget._multivol.set_background(settings.BACKGROUND_COLOR)

    def _toggle_clip(self, *args):
        if hasattr(self._vispy_widget, '_multivol'):
            self._update_clip()
