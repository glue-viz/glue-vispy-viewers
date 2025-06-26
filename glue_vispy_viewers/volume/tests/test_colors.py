from re import sub

from glue.config import LinearStretch, colormaps
from glue_vispy_viewers.volume.colors import create_cmap_template, get_mpl_cmap, \
                                             get_translucent_cmap, glsl_for_stretch


def clean_template(template):
    return sub("( |\n)", "", template)


def test_create_cmap_template():

    n_colors = 4
    stretch = LinearStretch()
    stretch_glsl = glsl_for_stretch(stretch)
    template = clean_template(create_cmap_template(n=n_colors, stretch_glsl=stretch_glsl))

    # vispy adds some extra code to the GLSL map for mapping bad values (e.g. NaN)
    # to a default color, so we need to account for that.
    # If this becomes more complicated we could use a regex, but with all of the parentheses
    # and brackets this feels simpler
    template_start = clean_template("vec4 translucent_colormap(float t) {")
    template_end = clean_template("""
        float s = t;
        if (s <= 0.25)
            { return $color_0; }
        if (s <= 0.5)
            { return $color_1; }
        if (s <= 0.75)
            { return $color_2; }
        return $color_3;
    }
    """)
    assert template.startswith(template_start)
    assert template.endswith(template_end)


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
    stretch_glsl = glsl_for_stretch(stretch)
    cmap = get_mpl_cmap(colormap, stretch)
    assert len(cmap.colors) == 256

    template = create_cmap_template(256, stretch_glsl)
    template_start, template_end = [clean_template(t) for t in template.split("\n", maxsplit=1)]
    template = clean_template(template)
    assert template.startswith(template_start)
    assert template.endswith(template_end)


def test_listed_cmap():

    colormap = colormaps['Viridis']
    stretch = LinearStretch()
    stretch_glsl = glsl_for_stretch(stretch)
    cmap = get_mpl_cmap(colormap, stretch)
    n_colors = len(colormap.colors)
    assert len(cmap.colors) == n_colors

    template = create_cmap_template(n_colors, stretch_glsl)
    template_start, template_end = [clean_template(t) for t in template.split("\n", maxsplit=1)]
    template = clean_template(template)
    assert template.startswith(template_start)
    assert template.endswith(template_end)
