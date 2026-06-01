import pytest

pytest.importorskip("glue_jupyter", exc_type=ImportError)
pytest.importorskip("solara", exc_type=ImportError)
pytest.importorskip("playwright", exc_type=ImportError)
pytest.importorskip("jupyter_rfb", exc_type=ImportError)

# Pin the vispy backend to jupyter_rfb so that figure_widget is a real
# DOMWidget. Vispy's default selection can fall through to glfw when an
# imported Qt binding fails to initialise (e.g. missing libEGL), which
# yields a non-widget that solara/ipywidgets cannot serialise.
import vispy  # noqa: E402
try:
    vispy.use(app='jupyter_rfb')
except RuntimeError:
    # vispy.use raises if a backend is already locked in. That's fine as
    # long as the locked-in backend is jupyter_rfb.
    if vispy.app.use_app().backend_name.lower() != 'jupyter_rfb':
        raise

from glue_jupyter import jglue  # noqa: E402

from ....tests.helpers import visual_test_jupyter  # noqa: E402
from ...tests import scenes  # noqa: E402
from ..scatter_viewer import JupyterVispyScatterViewer  # noqa: E402


@visual_test_jupyter(tolerance=5)
def test_visual_scatter3d_jupyter(tmp_path, page_session, solara_test):
    from ipywidgets import VBox
    data = scenes.basic_scatter3d_data()
    app = jglue()
    app.add_data(data)
    viewer = app.new_data_viewer(JupyterVispyScatterViewer, data=data)
    scenes.basic_scatter3d(viewer)
    # figure_widget is a raw vispy CanvasBackend (jupyter_rfb). Wrap it in a
    # DOMWidget so visual_test_jupyter can call add_class() on it.
    box = VBox([viewer.figure_widget])
    box.layout = {"width": "500px", "height": "500px"}
    return box
