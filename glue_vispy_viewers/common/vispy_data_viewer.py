import numpy as np

from echo import delay_callback

from vispy.util import keys

from .vispy_widget import VispyWidgetHelper
from .viewer_state import Vispy3DViewerState
from .compat import update_viewer_state


class BaseVispyViewerMixin:

    _state_cls = Vispy3DViewerState

    tools = ['vispy:reset', 'vispy:rotate']

    def setup_widget_and_callbacks(self):

        self._vispy_widget = VispyWidgetHelper(viewer_state=self.state)

        self.state.add_callback('clip_data', self._update_clip)
        self.state.add_callback('x_min', self._update_clip)
        self.state.add_callback('x_max', self._update_clip)
        self.state.add_callback('y_min', self._update_clip)
        self.state.add_callback('y_max', self._update_clip)
        self.state.add_callback('z_min', self._update_clip)
        self.state.add_callback('z_max', self._update_clip)

        self.state.add_callback('line_width', self._update_line_width)

        self.status_label = None
        self._opengl_ok = None
        self._ready_draw = False

        viewbox = self._vispy_widget.view.camera.viewbox

        viewbox.events.mouse_wheel.connect(self.camera_mouse_wheel)
        viewbox.events.mouse_move.connect(self.camera_mouse_move)
        viewbox.events.mouse_press.connect(self.camera_mouse_press)
        viewbox.events.mouse_release.connect(self.camera_mouse_release)

    def _update_appearance_from_settings(self, message):
        self._vispy_widget._update_appearance_from_settings()

    def redraw(self):
        if self._ready_draw:
            self._vispy_widget.canvas.render()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, layer=layer, layer_state=layer_state)

    def _update_clip(self, *args):
        for layer_artist in self._layer_artist_container:
            if self.state.clip_data:
                layer_artist.set_clip(self.state.clip_limits)
            else:
                layer_artist.set_clip(None)

    @staticmethod
    def update_viewer_state(rec, context):
        return update_viewer_state(rec, context)

    def camera_mouse_wheel(self, event=None):

        scale = (1.1 ** - event.delta[1])

        with delay_callback(self.state, 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):

            xmid = 0.5 * (self.state.x_min + self.state.x_max)
            dx = (self.state.x_max - xmid) * scale
            self.state.x_min = xmid - dx
            self.state.x_max = xmid + dx

            ymid = 0.5 * (self.state.y_min + self.state.y_max)
            dy = (self.state.y_max - ymid) * scale
            self.state.y_min = ymid - dy
            self.state.y_max = ymid + dy

            zmid = 0.5 * (self.state.z_min + self.state.z_max)
            dz = (self.state.z_max - zmid) * scale
            self.state.z_min = zmid - dz
            self.state.z_max = zmid + dz

        self._update_clip()

        event.handled = True

    def camera_mouse_press(self, event=None):

        self._initial_position = (self.state.x_min, self.state.x_max,
                                  self.state.y_min, self.state.y_max,
                                  self.state.z_min, self.state.z_max)

        self._width = (self.state.x_max - self.state.x_min,
                       self.state.y_max - self.state.y_min,
                       self.state.z_max - self.state.z_min)

    def camera_mouse_release(self, event=None):
        self._initial_position = None
        self._width = None

    def camera_mouse_move(self, event=None):

        if 1 in event.buttons and keys.SHIFT in event.mouse_event.modifiers:

            camera = self._vispy_widget.view.camera

            norm = np.mean(camera._viewbox.size)

            p1 = event.mouse_event.press_event.pos
            p2 = event.mouse_event.pos

            dist = (p1 - p2) / norm * camera._scale_factor
            dist[1] *= -1
            dx, dy, dz = camera._dist_to_trans(dist)

            with delay_callback(self.state, 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):

                self.state.x_min = self._initial_position[0] + self._width[0] * dx
                self.state.x_max = self._initial_position[1] + self._width[0] * dx
                self.state.y_min = self._initial_position[2] + self._width[1] * dy
                self.state.y_max = self._initial_position[3] + self._width[1] * dy
                self.state.z_min = self._initial_position[4] + self._width[2] * dz
                self.state.z_max = self._initial_position[5] + self._width[2] * dz

            event.handled = True

    def _update_line_width(self, *args):
        if hasattr(self._vispy_widget, '_multiscat'):
            self._vispy_widget._multiscat.update_line_width(self.state.line_width)
