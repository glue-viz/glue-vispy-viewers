import numpy as np

from glue.core import Data, DataCollection
from glue.core.application_base import Application

from ...tests.helpers import inverted_glue_colors, set_canvas_size, visual_test
from ..scatter_viewer import SimpleVispyScatterViewer
from . import scenes


def _make_viewer(data, extra_data=()):
    app = Application(DataCollection([data, *extra_data]))
    viewer = app.new_data_viewer(SimpleVispyScatterViewer, data=data)
    set_canvas_size(viewer, 500, 500)
    return app, viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_basic():
    data = scenes.basic_scatter3d_data()
    _, viewer = _make_viewer(data)
    scenes.basic_scatter3d(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_size_and_color():
    # Smaller cloud (n=150) so individual point sizes are distinguishable;
    # at n=500 the size variation drowns in marker overlap. Rendered with
    # inverted glue colours (black canvas, white axes) -- the viridis
    # colormap reads more clearly on a dark background, and this gives
    # scatter the same dark-theme coverage that the volume colormap test
    # exercises.
    with inverted_glue_colors():
        data = scenes.basic_scatter3d_data(n=150)
        _, viewer = _make_viewer(data)
        scenes.scatter3d_size_and_color(viewer, data)
        return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_subset():
    data = scenes.basic_scatter3d_data()
    app, viewer = _make_viewer(data)
    scenes.scatter3d_with_subset(app, viewer, data)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_two_layers():
    data = scenes.basic_scatter3d_data()
    np.random.seed(54321)
    data2 = Data(
        x=np.random.normal(0, 1, 200) + 1.5,
        y=np.random.normal(0, 1, 200) - 1.5,
        z=np.random.normal(0, 1, 200),
        label='cloud2',
    )
    app, viewer = _make_viewer(data, extra_data=[data2])
    scenes.scatter3d_two_layers(app, viewer, data, data2)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_vectors():
    data = scenes.basic_scatter3d_data(n=40)
    _, viewer = _make_viewer(data)
    scenes.scatter3d_vectors(viewer, data)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_errorbars():
    data = scenes.basic_scatter3d_data(n=40)
    _, viewer = _make_viewer(data)
    scenes.scatter3d_errorbars(viewer, data)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_rotated():
    data = scenes.basic_scatter3d_data()
    _, viewer = _make_viewer(data)
    scenes.scatter3d_rotated(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_scatter3d_perspective():
    data = scenes.basic_scatter3d_data()
    _, viewer = _make_viewer(data)
    scenes.scatter3d_perspective(viewer)
    return viewer
