import numpy as np

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
from echo import delay_callback

from qtpy import QtWidgets
from qtpy.QtCore import Qt

from vispy.util import keys

from .vispy_widget import VispyWidgetHelper
from .viewer_options import VispyOptionsWidget
from .toolbar import VispyViewerToolbar
from .viewer_state import Vispy3DViewerState
from .compat import update_viewer_state

BROKEN_PYQT5_MESSAGE = ("The version of PyQt5 you are using does not appear to "
                        "support OpenGL. See <a href='http://docs.glueviz.org/en"
                        "/stable/known_issues.html#d-viewers-not-working-on-linux"
                        "-with-pyqt5'>here</a> for more information about fixing "
                        "this issue.")


class BaseVispyViewer(DataViewerWithState):

    _state_cls = Vispy3DViewerState
    _toolbar_cls = VispyViewerToolbar
    _options_cls = VispyOptionsWidget

    tools = ['vispy:reset', 'vispy:rotate']
    subtools = {'save': ['vispy:save']}

    # If imageio is available, we can add the record icon
    try:
        import imageio  # noqa
    except ImportError:
        pass
    else:
        tools.insert(1, 'vispy:record')

    def __init__(self, session, state=None, parent=None):

        super(BaseVispyViewer, self).__init__(session, state=state, parent=parent)

        self._vispy_widget = VispyWidgetHelper(viewer_state=self.state)
        self.setCentralWidget(self._vispy_widget.canvas.native)

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

    def paintEvent(self, *args, **kwargs):
        super(BaseVispyViewer, self).paintEvent(*args, **kwargs)
        if self._opengl_ok is None:
            self._opengl_ok = self._vispy_widget.canvas.native.context() is not None
            if not self._opengl_ok:
                QtWidgets.QMessageBox.critical(self, "Error", BROKEN_PYQT5_MESSAGE)
                self.close(warn=False)
                self._vispy_widget.canvas.native.close()

    def _update_appearance_from_settings(self, message):
        self._vispy_widget._update_appearance_from_settings()

    def redraw(self):
        if self._ready_draw:
            self._vispy_widget.canvas.render()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, layer=layer, layer_state=layer_state)

    def show_status(self, text):
        statusbar = self.statusBar()
        statusbar.showMessage(text)

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

    def show(self):

        # WORKAROUND:
        # Due to a bug in Qt5, a hidden toolbar in glue causes a grey
        # rectangle to be overlaid on top of the glue window. Therefore
        # we check if the toolbar is hidden, and if so we make it into a
        # floating toolbar temporarily - still hidden, so this will not
        # be noticeable to the user.

        # tbar.setAllowedAreas(Qt.NoToolBarArea)

        if self._session.application is not None:
            tbar = self._session.application._mode_toolbar
            hidden = tbar.isHidden()
            if hidden:
                original_flags = tbar.windowFlags()
                tbar.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        else:
            hidden = False

        super(BaseVispyViewer, self).show()

        if hidden:
            tbar.setWindowFlags(original_flags)
            tbar.hide()

    def _update_line_width(self, *args):
        if hasattr(self._vispy_widget, '_multiscat'):
            self._vispy_widget._multiscat.update_line_width(self.state.line_width)
