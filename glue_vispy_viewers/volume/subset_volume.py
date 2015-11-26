import numpy as np

from vispy.color import Colormap

from vispy.visuals.volume import frag_dict, FRAG_SHADER, VolumeVisual
from vispy.scene.visuals import create_visual_node
from vispy.gloo import Texture3D, TextureEmulated3D

from matplotlib.colors import ColorConverter

converter = ColorConverter()

ADDITIVE_SNIPPETS_RGBA = dict(
    before_loop="""
        vec4 integrated_color = vec4(0., 0., 0., 0.);
        """,
    in_loop="""
        // We keep this in to avoid errors with cmap not being needed
        color = $cmap(val);

        color = $sample(u_volumetex, loc);

        integrated_color = 1.0 - (1.0 - integrated_color) * (1.0 - color);
        """,
    after_loop="""
        gl_FragColor = integrated_color;
        """,
)
ADDITIVE_FRAG_SHADER_RGBA = FRAG_SHADER.format(**ADDITIVE_SNIPPETS_RGBA)

frag_dict['additive_rgba'] = ADDITIVE_FRAG_SHADER_RGBA


def get_combined_data(data, clim, subsets):

    # Normalize the data to the 0-1 range
    data = (data - clim[0]) / (clim[1] - clim[0])
    data = np.clip(data, 0., 1.)

    n_subsets = len(subsets)

    combined_data = np.zeros(data.shape + (4,), dtype=np.float32)
    combined_data[:, :, :, 3] = data

    weight = np.zeros_like(data)

    for isubset, subset in enumerate(subsets):

        mask = subset['mask']

        color = np.array(converter.to_rgb(subset['color']))

        print(isubset, color)

        if len(color) == 3:
            color = np.hstack([color, 0.5])

        for channel in range(3):
            combined_data[..., channel][mask] += data[mask] * color[channel]
        weight[mask] += 1

    for channel in range(3):
        combined_data[..., channel][weight == 0] = combined_data[..., 3][weight == 0]
        combined_data[..., channel][weight > 0] /= weight[weight > 0]

    return combined_data


if __name__ == "__main__":

    from astropy.io import fits
    from vispy import scene

    # Read in data
    data = fits.getdata('https://astropy.stsci.edu/data/l1448/l1448_13co.fits').astype(np.float32)

    canvas = scene.SceneCanvas(show=True)
    view = canvas.central_widget.add_view()

    subsets = [{'mask': data > 2, 'color': 'red'}, {'mask': data > 1.5, 'color': 'blue'}]
    # subsets = []

    combined_data = get_combined_data(data, (0, 12), subsets)

    volume = scene.visuals.Volume(combined_data, parent=view.scene, method='additive_rgba', clim=(0, 1))

    view.camera = scene.cameras.TurntableCamera(parent=view.scene)

    canvas.render()
