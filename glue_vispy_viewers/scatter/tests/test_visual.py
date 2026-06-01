from glue.core import DataCollection
from glue.core.application_base import Application

from ...tests.helpers import set_canvas_size, visual_test
from ..scatter_viewer import SimpleVispyScatterViewer
from . import scenes


def _make_viewer(data):
    app = Application(DataCollection([data]))
    viewer = app.new_data_viewer(SimpleVispyScatterViewer, data=data)
    set_canvas_size(viewer, 500, 500)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_basic():
    data = scenes.basic_scatter3d_data()
    viewer = _make_viewer(data)
    scenes.basic_scatter3d(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_colormap():
    data = scenes.basic_scatter3d_data()
    viewer = _make_viewer(data)
    scenes.scatter3d_colormap(viewer, data)
    return viewer
