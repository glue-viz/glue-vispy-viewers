from __future__ import absolute_import, division, print_function

import numpy as np

from glue.config import settings

from qtpy.QtWidgets import QMessageBox
from qtpy.QtCore import QTimer
from glue.external.echo import delay_callback

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

        self._vispy_widget.canvas.events.mouse_press.connect(self.mouse_press)
        self._vispy_widget.canvas.events.mouse_wheel.connect(self.mouse_wheel)
        self._vispy_widget.canvas.events.mouse_release.connect(self.mouse_release)

        self._vispy_widget.view.camera.viewbox.events.mouse_wheel.connect(self.camera_mouse_wheel)

        self._downsampled = False

        # For the mouse wheel, we receive discrete events so we need to have
        # a buffer (for now 250ms) before which we consider the mouse wheel
        # event to have stopped.

        self._downsample_timer = QTimer()
        self._downsample_timer.setInterval(250)
        self._downsample_timer.setSingleShot(True)
        self._downsample_timer.timeout.connect(self.mouse_release)

        # We do this here in addition to in the volume viewer itself as for
        # some situations e.g. reloading from session files, a clip_data event
        # isn't emitted.
        self._update_clip(force=True)

    def camera_mouse_wheel(self, event=None):

        scale = (1.1 ** - event.delta[1])

        with delay_callback(self.state, 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):

            xmid = 0.5 * (self.state.x_min + self.state.x_max)
            dx = (self.state.x_max - xmid) * scale
            self.state.x_min = xmid - dx
            self.state.x_max = xmid + dx

            ymid = 0.5 * (self.state.y_min + self.state.y_max)
            dy = (self.state.y_max - xmid) * scale
            self.state.y_min = ymid - dy
            self.state.y_max = ymid + dy

            zmid = 0.5 * (self.state.z_min + self.state.z_max)
            dz = (self.state.z_max - zmid) * scale
            self.state.z_min = zmid - dz
            self.state.z_max = zmid + dz

        self._update_clip()

        event.handled = True

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
        if self.state.clip_data or force:
            coords = np.array([[-1, -1, -1], [1, 1, 1]])
            coords = self._vispy_widget._multivol.transform.imap(coords)[:,:3] / 128.
            self._vispy_widget._multivol.set_clip(self.state.clip_data, coords.ravel())

    def _update_slice_transform(self):

        self._vispy_widget._multivol._update_slice_transform(self.state.x_min, self.state.x_max,
                                               self.state.y_min, self.state.y_max,
                                               self.state.z_min, self.state.z_max)

    def mouse_wheel(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol'):
                if not self._downsampled:
                    self.mouse_press()
                self._downsample_timer.start()

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
