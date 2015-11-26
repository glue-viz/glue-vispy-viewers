import numpy as np

from vispy.color import Colormap

from vispy.visuals.volume import frag_dict, FRAG_SHADER, VolumeVisual
from vispy.scene.visuals import create_visual_node
from vispy.gloo import Texture3D, TextureEmulated3D

from matplotlib.colors import ColorConverter

converter = ColorConverter()

GLUE_SNIPPETS = dict(
    before_loop="""
        vec4 integrated_color = vec4(0., 0., 0., 0.);
        float weight = 0;
        float weight_sum = 0;
        float tau = 0;
        """,
    in_loop="""
            color = $cmap(val);
            weight = (1.0 - tau) * color.w / 20;
            integrated_color = integrated_color + color * weight;
            tau += weight;
            if(tau > 1.0) tau = 1.;
        """,
    after_loop="""
        gl_FragColor = integrated_color;
        """,
)
GLUE_FRAG_SHADER = FRAG_SHADER.format(**GLUE_SNIPPETS)

frag_dict['glue'] = GLUE_FRAG_SHADER

N_SUBSET_MAX = 9

BLACK = np.array([0, 0, 0, 0])

def get_data_cmap_clim(data, clim, subsets):

    # Now we normalize the data to the 0-1 range
    data = (data - clim[0]) / (clim[1] - clim[0])
    data = np.clip(data, 0., 0.99)

    n_subsets = len(subsets)

    # Next, we can add an integer to the values for different subsets. We leave an
    # interval of D between each dataset and subset to avoid boundary issues.
    # Essentially in data value space, we have this:

    # 0          1   1 + D          2 + D   2 + 2D            3 + 2D
    # |-- DATA --|   | --- SUBSET 1 ----|   | --- SUBSET 2 --------|

    D = 0.2

    clim = (0, 1 + n_subsets * (1 + D))

    colors = [np.array([1, 1, 1, 0]), np.array([1, 1, 1, 1])]
    controls = [0, 1 / clim[1]]

    for isubset, subset in enumerate(subsets):

        # Only modify pixels that haven't already been modified
        mask = subset['mask'].copy()
        mask[data > 1] = False

        data[mask] += (isubset + 1)

        colors.append(BLACK)
        colors.append(BLACK)

        color = np.array(converter.to_rgb(subset['color']))

        colors.append(np.hstack([color, 0]))
        colors.append(np.hstack([color, 1]))

        controls.append((1 + isubset) / clim[1])
        controls.append(((1 + isubset) * (1 + D)) / clim[1])
        controls.append(((1 + isubset) * (1 + D)) / clim[1])
        controls.append((1 + (1 + isubset) * (1 + D)) / clim[1])

    cmap_subset = Colormap(colors, controls=controls)

    return data, clim, cmap_subset


class SubsetVolumeVisual(VolumeVisual):

    def __init__(self, data, subsets, clim=None, emulate_texture=False):

        data, clim, cmap = get_data_cmap_clim(data, clim, subsets)

        super(SubsetVolumeVisual, self).__init__(data, clim=clim, cmap=cmap, emulate_texture=emulate_texture, method='glue')

        tex_cls = TextureEmulated3D if emulate_texture else Texture3D

        self._tex = tex_cls((10, 10, 10), interpolation='nearest',
                            wrapping='clamp_to_edge')

        self._program['u_volumetex'] = self._tex

        self.set_data(data, clim=clim)

    def set_data_and_subsets(self, data, clim, subsets):
        data, clim, self.cmap = get_data_cmap_clim(data, clim, subsets)
        super(SubsetVolumeVisual, self).set_data(data, clim)

SubsetVolume = create_visual_node(SubsetVolumeVisual)


if __name__ == "__main__":

    from astropy.io import fits
    from vispy import scene

    # Read in data
    data = fits.getdata('https://astropy.stsci.edu/data/l1448/l1448_13co.fits')

    canvas = scene.SceneCanvas(show=True)
    view = canvas.central_widget.add_view()

    subsets = [{'mask': data > 2, 'color':'red'}, {'mask': data > 1, 'color':'blue'}]
    # subsets = [{'mask': data > 2, 'color':'red'}]
    volume = SubsetVolume(data, subsets, clim=(0, 3), parent=view.scene, emulate_texture=False)
    # volume = scene.visuals.Volume(data, clim=clim, parent=view.scene, emulate_texture=False, cmap=cmap_subset, method='glue')
    view.camera = scene.cameras.TurntableCamera(parent=view.scene)

    canvas.render()
