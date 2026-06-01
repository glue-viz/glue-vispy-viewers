"""
Scene builders shared by the scatter visual tests at every layer.

Each viewer host (backend-independent, Qt, Jupyter) constructs its own
viewer and then hands it to one of these functions to configure state.
This keeps the actual scene definition in one place, so a Qt-vs-Jupyter
divergence shows up as a baseline-image diff at exactly the test that
covers that scene.
"""

import numpy as np

from glue.core import Data
from glue.core.link_helpers import LinkSame


def basic_scatter3d_data(seed=12345, n=500):
    np.random.seed(seed)
    return Data(
        x=np.random.normal(0, 1, n),
        y=np.random.normal(0, 1, n),
        z=np.random.normal(0, 1, n),
        label='cloud',
    )


def basic_scatter3d(viewer):
    """
    Basic gaussian point cloud, fixed limits, crimson markers.

    Assumes the data from ``basic_scatter3d_data`` has already been added
    to the viewer (so ``viewer.state.layers[0]`` exists).
    """
    viewer.state.x_min, viewer.state.x_max = -3, 3
    viewer.state.y_min, viewer.state.y_max = -3, 3
    viewer.state.z_min, viewer.state.z_max = -3, 3
    viewer.state.layers[0].color = 'crimson'
    viewer.state.layers[0].size = 4


def scatter3d_size_and_color(viewer, data):
    """
    Linear size mapping by radial distance, linear viridis colormap by x.

    Using *different* attributes for size and color is deliberate: it catches
    bugs where size_att and cmap_att could bleed into each other. A correct
    render shows small-to-big circles from origin outward AND a left-to-right
    color gradient; if they were the same attribute, the size gradient would
    align with the color gradient and the bug would be invisible.
    """
    basic_scatter3d(viewer)
    r = np.hypot(np.hypot(data['x'], data['y']), data['z'])
    data.add_component(r, label='r')

    import matplotlib.pyplot as plt
    layer = viewer.state.layers[0]
    layer.size_mode = 'Linear'
    layer.size_att = data.id['r']
    layer.size_vmin = 0
    layer.size_vmax = 4
    layer.size_scaling = 1
    layer.color_mode = 'Linear'
    layer.cmap_att = data.id['x']
    layer.cmap_vmin = -3
    layer.cmap_vmax = 3
    layer.cmap = plt.cm.viridis


def scatter3d_with_subset(app, viewer, data):
    """Basic scene with an inner-sphere subset highlighted."""
    basic_scatter3d(viewer)
    # The default subset color is red, which would blend into the crimson
    # main layer; dim the main layer so the subset stands out.
    viewer.state.layers[0].color = '#bbbbbb'
    app.data_collection.new_subset_group(
        label='inner',
        subset_state=(data.id['x'] ** 2 + data.id['y'] ** 2 + data.id['z'] ** 2) < 1,
    )
    # Subset layer is layer index 1; make it distinct.
    viewer.state.layers[1].color = 'orange'
    viewer.state.layers[1].size = 6


def scatter3d_two_layers(app, viewer, data, data2):
    """Two linked data sets in the same viewer, distinct colors."""
    basic_scatter3d(viewer)
    app.data_collection.add_link(LinkSame(data.id['x'], data2.id['x']))
    app.data_collection.add_link(LinkSame(data.id['y'], data2.id['y']))
    app.data_collection.add_link(LinkSame(data.id['z'], data2.id['z']))
    viewer.add_data(data2)
    viewer.state.layers[1].color = 'royalblue'
    viewer.state.layers[1].size = 4


def scatter3d_vectors(viewer, data):
    """Sparse cloud with outward-pointing 3D vectors."""
    basic_scatter3d(viewer)
    r = np.hypot(np.hypot(data['x'], data['y']), data['z'])
    inv = 1.0 / np.maximum(r, 1e-3)
    data.add_component(data['x'] * inv, label='vx')
    data.add_component(data['y'] * inv, label='vy')
    data.add_component(data['z'] * inv, label='vz')

    layer = viewer.state.layers[0]
    layer.vector_visible = True
    layer.vx_att = data.id['vx']
    layer.vy_att = data.id['vy']
    layer.vz_att = data.id['vz']
    layer.vector_scaling = 0.5


def scatter3d_errorbars(viewer, data):
    """Sparse cloud with per-point error bars on x, y, and z, each driven
    by a *different* attribute so the test catches xerr/yerr/zerr routing
    bugs that a single shared error attribute would mask.
    """
    basic_scatter3d(viewer)
    n = len(data['x'])
    # Three distinct per-point error patterns: linear ramp on x, |x|-based
    # on y, and |z|-based on z. Each axis pulls from its own component.
    data.add_component(np.linspace(0.1, 0.6, n), label='xerr')
    data.add_component(0.2 + 0.4 * np.abs(data['x']) / 3, label='yerr')
    data.add_component(0.15 + 0.35 * np.abs(data['z']) / 3, label='zerr')

    layer = viewer.state.layers[0]
    layer.xerr_visible = True
    layer.xerr_att = data.id['xerr']
    layer.yerr_visible = True
    layer.yerr_att = data.id['yerr']
    layer.zerr_visible = True
    layer.zerr_att = data.id['zerr']


def scatter3d_clip_off(viewer):
    """Tight limits with the cloud overflowing them and ``clip_data=False``.

    The basic test uses clip_data=True (default) and shows nothing outside
    the bounding box. Turning it off should let those overflow points
    render past the cube; that visible overflow is what proves the
    clip_data toggle reaches the layer artist.
    """
    viewer.state.x_min, viewer.state.x_max = -1.5, 1.5
    viewer.state.y_min, viewer.state.y_max = -1.5, 1.5
    viewer.state.z_min, viewer.state.z_max = -1.5, 1.5
    viewer.state.clip_data = False
    viewer.state.layers[0].color = 'crimson'
    viewer.state.layers[0].size = 4


def anisotropic_scatter3d_data(seed=12345, n=400):
    """Gaussian cloud with very different per-axis ranges.

    Used to make ``native_aspect`` visibly non-cubic: x is roughly 4x
    wider than y, and z sits in between.
    """
    np.random.seed(seed)
    return Data(
        x=np.random.normal(0, 4.0, n),
        y=np.random.normal(0, 1.0, n),
        z=np.random.normal(0, 2.0, n),
        label='anisotropic',
    )


def scatter3d_native_aspect(viewer):
    """Anisotropic cloud with ``native_aspect`` on so the box matches
    the data's per-axis range -- expect a wide, shallow bounding box."""
    viewer.state.x_min, viewer.state.x_max = -12, 12
    viewer.state.y_min, viewer.state.y_max = -3, 3
    viewer.state.z_min, viewer.state.z_max = -6, 6
    viewer.state.layers[0].color = 'crimson'
    viewer.state.layers[0].size = 4
    viewer.state.native_aspect = True


def scatter3d_rotated(viewer, azimuth=60, elevation=15):
    """Basic scene viewed from a non-default camera angle."""
    basic_scatter3d(viewer)
    camera = viewer._vispy_widget.view.camera
    camera.azimuth = azimuth
    camera.elevation = elevation
    camera.view_changed()


def scatter3d_perspective(viewer):
    """Basic scene rendered in perspective projection rather than orthographic."""
    basic_scatter3d(viewer)
    viewer.state.perspective_view = True
