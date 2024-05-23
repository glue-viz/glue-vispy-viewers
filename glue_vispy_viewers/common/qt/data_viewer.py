from glue_qt.viewers.common.data_viewer import DataViewer

from qtpy import QtWidgets

from .viewer_options import VispyOptionsWidget

from ..vispy_data_viewer import BaseVispyViewerMixin

from .toolbar import VispyQtToolbar

from . import tools  # noqa

BROKEN_PYQT5_MESSAGE = ("The version of PyQt5 you are using does not appear to "
                        "support OpenGL. See <a href='http://docs.glueviz.org/en"
                        "/stable/known_issues.html#d-viewers-not-working-on-linux"
                        "-with-pyqt5'>here</a> for more information about fixing "
                        "this issue.")


class BaseVispyViewer(BaseVispyViewerMixin, DataViewer):

    _options_cls = VispyOptionsWidget
    subtools = {'save': ['vispy:save']}

    _toolbar_cls = VispyQtToolbar

    def __init__(self, session, state=None, parent=None):
        super().__init__(session, state=state, parent=parent)
        self.setup_widget_and_callbacks()
        self.setCentralWidget(self._vispy_widget.canvas.native)

    def paintEvent(self, *args, **kwargs):
        super().paintEvent(*args, **kwargs)
        if self._opengl_ok is None:
            self._opengl_ok = self._vispy_widget.canvas.native.context() is not None
            if not self._opengl_ok:
                QtWidgets.QMessageBox.critical(self, "Error", BROKEN_PYQT5_MESSAGE)
                self.close(warn=False)
                self._vispy_widget.canvas.native.close()

    def show_status(self, text):
        statusbar = self.statusBar()
        statusbar.showMessage(text)


# If imageio is available, we can add the record icon
try:
    import imageio  # noqa
except ImportError:
    pass
else:
    BaseVispyViewer.tools = BaseVispyViewer.tools[:] + ['vispy:record']
