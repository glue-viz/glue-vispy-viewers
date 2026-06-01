import pytest

pytest.importorskip("qtpy.QtWidgets", exc_type=ImportError)
pytest.importorskip("glue_qt.app.application", exc_type=ImportError)

from glue.core import DataCollection  # noqa: E402
from glue_qt.app.application import GlueApplication  # noqa: E402

from ....tests.helpers import set_canvas_size, visual_test_qt  # noqa: E402
from ...tests import scenes  # noqa: E402
from ..scatter_viewer import VispyScatterViewer  # noqa: E402


@visual_test_qt(tolerance=5)
def test_visual_scatter3d_qt():
    data = scenes.basic_scatter3d_data()
    ga = GlueApplication(DataCollection([data]))
    ga.show()
    viewer = ga.new_data_viewer(VispyScatterViewer, data=data)
    set_canvas_size(viewer, 500, 500)
    scenes.basic_scatter3d(viewer)
    return viewer
