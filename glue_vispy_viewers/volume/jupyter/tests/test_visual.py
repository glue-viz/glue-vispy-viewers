import pytest

pytest.importorskip("glue_jupyter", exc_type=ImportError)
pytest.importorskip("solara", exc_type=ImportError)
pytest.importorskip("playwright", exc_type=ImportError)
pytest.importorskip("jupyter_rfb", exc_type=ImportError)

# Pin the vispy backend to jupyter_rfb before importing helpers.py (which
# would otherwise lock vispy to glfw). Tolerate re-imports.
import vispy  # noqa: E402
try:
    vispy.use(app='jupyter_rfb')
except RuntimeError:
    if vispy.app.use_app().backend_name.lower() != 'jupyter_rfb':
        raise

from glue.core import DataCollection  # noqa: E402
from glue_jupyter import JupyterApplication  # noqa: E402

from ....tests.helpers import visual_test_jupyter  # noqa: E402
from ...tests import scenes  # noqa: E402
from ..volume_viewer import JupyterVispyVolumeViewer  # noqa: E402


@visual_test_jupyter(tolerance=5)
def test_visual_volume3d_jupyter(tmp_path, page_session, solara_test):
    from ipywidgets import VBox
    data = scenes.blob_data()
    app = JupyterApplication(DataCollection([data]))
    viewer = app.new_data_viewer(JupyterVispyVolumeViewer, data=data)
    scenes.basic_volume(viewer)
    box = VBox([viewer.figure_widget])
    box.layout = {"width": "500px", "height": "500px"}
    return box
