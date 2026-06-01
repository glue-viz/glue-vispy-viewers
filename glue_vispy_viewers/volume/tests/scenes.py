"""
Scene builders shared by the volume visual tests at every layer.

Mirrors ``glue_vispy_viewers.scatter.tests.scenes`` — same pattern, same
purpose: keep scene definitions in one place so a Qt-vs-Jupyter divergence
shows up as a baseline-image diff at the exact scene that covers it.
"""

import numpy as np

from glue.core import Data
from glue.core.link_helpers import LinkSame


def blob_data(seed=12345, n=32, sigma=0.5):
    """3D cube containing a centred Gaussian blob plus one off-centre bump."""
    rng = np.random.RandomState(seed)
    x, y, z = np.mgrid[-1:1:n * 1j, -1:1:n * 1j, -1:1:n * 1j]

    # Centred blob
    blob = np.exp(-(x ** 2 + y ** 2 + z ** 2) / sigma ** 2)
    # Off-centre bump so colormaps/clipping produce asymmetric visuals
    bump = 0.6 * np.exp(-((x - 0.4) ** 2 + (y - 0.3) ** 2 + (z + 0.2) ** 2) / 0.08)
    intensity = (blob + bump + 0.02 * rng.standard_normal(blob.shape)).astype(np.float32)

    return Data(intensity=intensity, label='blob')


def scatter_overlay_data(seed=54321, n=80):
    """1D scatter data with x/y/z components in the same coord space as blob."""
    rng = np.random.RandomState(seed)
    return Data(
        x=rng.uniform(0, 31, n),
        y=rng.uniform(0, 31, n),
        z=rng.uniform(0, 31, n),
        label='markers',
    )


def basic_volume(viewer):
    """Default render — single volume, default colormap and opacity."""
    layer = viewer.state.layers[0]
    layer.v_min = 0
    layer.v_max = 1
    layer.alpha = 1.0


def volume_colormap(viewer):
    """Same blob with a vivid yellow-orange-red colormap.

    The translucent volume rendering ties alpha to cmap-position, which
    washes out cmaps whose mid-range is dark (plasma, viridis) -- a lot of
    semi-transparent colored voxels integrate to a muted result. YlOrRd
    has a saturated warm mid-range that survives ray accumulation, which
    is what we want for a regression test of "the cmap setting reaches
    the GPU".
    """
    import matplotlib.pyplot as plt
    basic_volume(viewer)
    layer = viewer.state.layers[0]
    # cmap only takes effect in Linear color mode; the default Fixed mode
    # uses layer.color and ignores cmap entirely.
    layer.color_mode = 'Linear'
    layer.cmap = plt.cm.YlOrRd
    layer.v_min = 0.1
    layer.v_max = 0.6


def volume_with_subset(app, viewer, data):
    """Volume with an inner-hemisphere subset highlighted."""
    basic_volume(viewer)
    # n=32, so half-cube subset is the lower-x voxels
    app.data_collection.new_subset_group(
        label='left half',
        subset_state=data.pixel_component_ids[0] < 16,
    )


def volume_clip_off(viewer):
    """Tight bounding box with ``clip_data=False`` so the blob extends past it.

    With clipping on (the default, exercised by the basic test) the
    sampled region is bounded by state.[xyz]_min/max. Turning clipping
    off makes the full texture render regardless -- the blob spills out
    past the cube, which is the visible signal that the toggle reaches
    ``MultiVolume.set_clip``.
    """
    basic_volume(viewer)
    # n=32, blob centred at voxel 16. Pull limits in tight so the box is
    # much smaller than the blob; turning clipping off should then show
    # the blob extending past the box.
    viewer.state.x_min, viewer.state.x_max = 12, 20
    viewer.state.y_min, viewer.state.y_max = 12, 20
    viewer.state.z_min, viewer.state.z_max = 12, 20
    viewer.state.clip_data = False


def volume_with_scatter_overlay(app, viewer, vol_data, scatter_data):
    """Volume rendering with a 1D scatter overlay."""
    basic_volume(viewer)
    app.data_collection.add_link(
        LinkSame(vol_data.pixel_component_ids[0], scatter_data.id['z'])
    )
    app.data_collection.add_link(
        LinkSame(vol_data.pixel_component_ids[1], scatter_data.id['y'])
    )
    app.data_collection.add_link(
        LinkSame(vol_data.pixel_component_ids[2], scatter_data.id['x'])
    )
    viewer.add_data(scatter_data)
    # Scatter layer is layer index 1 after the volume.
    viewer.state.layers[1].color = 'yellow'
    viewer.state.layers[1].size = 6
