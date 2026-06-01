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


def scatter3d_colormap(viewer, data):
    """
    Same point cloud with a linear viridis colormap driven by the
    radial distance from origin.
    """
    basic_scatter3d(viewer)
    r = np.hypot(np.hypot(data['x'], data['y']), data['z'])
    data.add_component(r, label='r')

    import matplotlib.pyplot as plt
    layer = viewer.state.layers[0]
    layer.color_mode = 'Linear'
    layer.cmap_att = data.id['r']
    layer.cmap_vmin = 0
    layer.cmap_vmax = 4
    layer.cmap = plt.cm.viridis
