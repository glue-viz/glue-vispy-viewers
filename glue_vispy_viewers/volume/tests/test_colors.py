from re import sub

from vispy.color.colormap import LUT_len
from glue.config import LinearStretch, colormaps
from glue_vispy_viewers.volume.colors import CustomColormap, get_mpl_cmap, \
                                             get_translucent_cmap


def clean_template(template):
    return sub("( |\n)", "", template)


def test_translucent_cmap():
    color = (0.3, 0.5, 0.7)
    stretch = LinearStretch()
    cmap_cls = get_translucent_cmap(*color, stretch)
    template = clean_template(cmap_cls.glsl_map)

    template_start = clean_template("vec4 translucent_fire(float t) {")
    template_end = clean_template("""
        return vec4(0.3, 0.5, 0.7, t);
    }
    """)
    assert template.startswith(template_start)
    assert template.endswith(template_end)


def test_linear_cmap():

    colormap = colormaps['Red-Blue']
    stretch = LinearStretch()
    cmap = get_mpl_cmap(colormap, stretch)
    assert isinstance(cmap, CustomColormap)
    assert cmap.texture_map_data.shape == (LUT_len, 1, 4)


def test_listed_cmap():

    colormap = colormaps['Viridis']
    stretch = LinearStretch()
    cmap = get_mpl_cmap(colormap, stretch)
    assert isinstance(cmap, CustomColormap)
    assert cmap.texture_map_data.shape == (LUT_len, 1, 4)
