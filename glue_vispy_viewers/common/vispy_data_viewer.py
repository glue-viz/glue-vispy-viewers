from __future__ import absolute_import, division, print_function

from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState

from glue.utils import nonpartial

from qtpy import PYQT5, QtWidgets

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

    tools = ['vispy:reset', 'vispy:save', 'vispy:rotate']

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

        self.state.add_callback('clip_data', nonpartial(self._toggle_clip))

        self.status_label = None
        self._opengl_ok = None
        self._ready_draw = False

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

    def _toggle_clip(self):
        for layer_artist in self._layer_artist_container:
            if self.state.clip_data:
                layer_artist.set_clip(self.state.clip_limits)
            else:
                layer_artist.set_clip(None)

    @staticmethod
    def update_viewer_state(rec, context):
        return update_viewer_state(rec, context)

    if PYQT5:

        def show(self):

            # WORKAROUND:
            # Due to a bug in Qt5, a hidden toolbar in glue causes a grey
            # rectangle to be overlaid on top of the glue window. Therefore
            # we check if the toolbar is hidden, and if so we make it into a
            # floating toolbar temporarily - still hidden, so this will not
            # be noticeable to the user.

            # tbar.setAllowedAreas(Qt.NoToolBarArea)

            from qtpy.QtCore import Qt

            tbar = self._session.application._mode_toolbar
            hidden = tbar.isHidden()

            if hidden:
                original_flags = tbar.windowFlags()
                tbar.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

            super(BaseVispyViewer, self).show()

            if hidden:
                tbar.setWindowFlags(original_flags)
                tbar.hide()
