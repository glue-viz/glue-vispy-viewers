import numpy as np
import pytest

from glue.core import DataCollection
from glue.core.application_base import Application

from ...tests.helpers import (HAS_VISUAL_TEST_DEPS, inverted_glue_colors,
                              set_canvas_size, visual_test)
from ..volume_viewer import SimpleVispyVolumeViewer
from . import scenes


def _make_viewer(data, extra_data=()):
    app = Application(DataCollection([data, *extra_data]))
    viewer = app.new_data_viewer(SimpleVispyVolumeViewer, data=data)
    set_canvas_size(viewer, 500, 500)
    return app, viewer


def _rendered_data_fraction(viewer):
    """Fraction of canvas pixels that differ from the background corner."""
    img = np.asarray(viewer._vispy_widget.canvas.render())[..., :3].astype(int)
    background = img[0, 0]
    return (np.abs(img - background).sum(-1) > 10).mean()


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS,
                    reason="requires Pillow, vispy[glfw] and a display")
def test_flip_axis_limit_keeps_volume_visible():
    # Regression test: flipping an axis limit (so x_min > x_max) gives the
    # limit transform a negative scale, which used to leave the clip box with
    # an inverted axis (min > max) so the shader clipped the whole volume away.
    # The data should stay visible after flipping each axis in turn.
    data = scenes.blob_data()
    _, viewer = _make_viewer(data)
    scenes.basic_volume(viewer)
    assert viewer.state.clip_data
    baseline = _rendered_data_fraction(viewer)
    assert baseline > 0.1
    try:
        for flip in (viewer.state.flip_x, viewer.state.flip_y, viewer.state.flip_z):
            flip()
            assert _rendered_data_fraction(viewer) > 0.5 * baseline
    finally:
        viewer.close()


@pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS,
                    reason="requires Pillow, vispy[glfw] and a display")
def test_cutting_plane_works_at_non_default_resolution():
    # The cutting plane lives in the shader cube which spans 0..resolution, so
    # a centred cut must remove roughly half the volume at any resolution --
    # not only the default 256. Also exercise changing the resolution while
    # the cut is active, which must refresh the plane uniforms.
    data = scenes.blob_data()
    _, viewer = _make_viewer(data)
    scenes.basic_volume(viewer)
    viewer.state.cut_enabled = True
    viewer.state.cut_mode = 'Simple'
    viewer.state.cut_axis = 'Z'
    viewer.state.cut_depth = 0.5
    try:
        # Switching resolution with the cut active must refresh the plane
        # uniforms; at each resolution the centred cut should still remove a
        # meaningful chunk of the volume.
        for resolution in (64, 256):
            viewer.state.resolution = resolution
            viewer.state.cut_enabled = False
            uncut = _rendered_data_fraction(viewer)
            viewer.state.cut_enabled = True
            cut = _rendered_data_fraction(viewer)
            assert uncut - cut > 0.05, (resolution, uncut, cut)
    finally:
        viewer.close()


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
def test_visual_volume3d_cutting_plane():
    # Exercises the cutting plane uniforms via the L1448 cube. Sets a
    # diagonal cut so a render with the plane disabled (or with the
    # uniforms wrong) would look obviously different from the baseline.
    with inverted_glue_colors():
        data = scenes.l1448_data()
        _, viewer = _make_viewer(data)
        scenes.volume_cutting_plane(viewer)
        return viewer


@visual_test(tolerance=5)
def test_visual_volume3d_cutting_plane_color():
    data = scenes.l1448_data()
    _, viewer = _make_viewer(data)
    scenes.volume_cutting_plane_bgcolor(viewer, "#686AED", 0.65)
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
