from glue.core import DataCollection
from glue.core.application_base import Application

from ...tests.helpers import inverted_glue_colors, set_canvas_size, visual_test
from ..volume_viewer import SimpleVispyVolumeViewer
from . import scenes


def _make_viewer(data, extra_data=()):
    app = Application(DataCollection([data, *extra_data]))
    viewer = app.new_data_viewer(SimpleVispyVolumeViewer, data=data)
    set_canvas_size(viewer, 500, 500)
    return app, viewer


@visual_test(tolerance=5)
def test_visual_volume3d_basic():
    data = scenes.blob_data()
    _, viewer = _make_viewer(data)
    scenes.basic_volume(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_colormap():
    # Real L1448 13CO datacube rendered against a dark canvas. The
    # inverted colours exercise the appearance-from-settings code path,
    # and real data exercises the load-from-FITS path that synthetic
    # blobs miss.
    with inverted_glue_colors():
        data = scenes.l1448_data()
        _, viewer = _make_viewer(data)
        scenes.volume_colormap(viewer)
        return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_native_aspect():
    data = scenes.l1448_data()
    _, viewer = _make_viewer(data)
    scenes.volume_native_aspect(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_subset():
    data = scenes.blob_data()
    app, viewer = _make_viewer(data)
    scenes.volume_with_subset(app, viewer, data)
    return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_clip_off():
    data = scenes.blob_data()
    _, viewer = _make_viewer(data)
    scenes.volume_clip_off(viewer)
    return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_scatter_overlay():
    vol_data = scenes.blob_data()
    scatter_data = scenes.scatter_overlay_data()
    app, viewer = _make_viewer(vol_data, extra_data=[scatter_data])
    scenes.volume_with_scatter_overlay(app, viewer, vol_data, scatter_data)
    return viewer
