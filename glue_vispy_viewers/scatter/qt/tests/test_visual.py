import pytest

pytest.importorskip("qtpy.QtWidgets", exc_type=ImportError)
pytest.importorskip("glue_qt.app.application", exc_type=ImportError)

# Pin the vispy backend to the active Qt binding before importing helpers.py
# (which would otherwise lock vispy to glfw at import time, leaving
# canvas.native as a glfw object instead of a QWidget). qtpy resolves to
# whichever Qt binding is installed, so this works for both PyQt6 and PySide6.
import vispy  # noqa: E402
import qtpy  # noqa: E402
try:
    vispy.use(app=qtpy.API_NAME)
except RuntimeError:
    if vispy.app.use_app().backend_name.lower() != qtpy.API_NAME.lower():
        raise

from glue.core import DataCollection  # noqa: E402
from glue_qt.app.application import GlueApplication  # noqa: E402

from ....tests.helpers import set_canvas_size, visual_test_qt  # noqa: E402
from ...tests import scenes  # noqa: E402
from ..scatter_viewer import VispyScatterViewer  # noqa: E402


class TestVispyScatterViewerQt:
    # Class-based so the GlueApplication and viewer live on self for the
    # duration of each test method. If they went out of scope between the
    # test body and the decorator's canvas.render(), Qt would destroy the
    # underlying CanvasBackendDesktop. This mirrors how glue-qt's own
    # viewer tests are organised.

    def setup_method(self, method):
        self.data = scenes.basic_scatter3d_data()
        self.app = GlueApplication(DataCollection([self.data]))
        self.app.show()
        self.viewer = self.app.new_data_viewer(VispyScatterViewer, data=self.data)
        set_canvas_size(self.viewer, 500, 500)

    def teardown_method(self, method):
        self.viewer.close()
        self.viewer = None
        self.app.close()
        self.app = None

    @visual_test_qt(tolerance=5)
    def test_visual_scatter3d_qt(self):
        scenes.basic_scatter3d(self.viewer)
        return self.viewer
