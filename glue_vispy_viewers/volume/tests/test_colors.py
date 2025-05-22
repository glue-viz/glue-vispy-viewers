from re import sub

from glue_vispy_viewers.volume.colors import create_cmap_template, get_translucent_cmap


def clean_template(template):
    return sub("(    |\n)", "", template)


def test_create_cmap_template():

    n_colors = 4
    template = create_cmap_template(n=n_colors)

    assert clean_template(template) == clean_template("""
    vec4 translucent_colormap(float t) {
        if (t <= 0.25)
            { return $color_0; }
        if (t <= 0.5)
            { return $color_1; }
        if (t <= 0.75)
            { return $color_2; }
        return $color_3;
    }
    """)


def test_translucent_cmap():
    color = (0.3, 0.5, 0.7)
    cmap_cls = get_translucent_cmap(*color)

    assert clean_template(cmap_cls.glsl_map) == clean_template("""
    vec4 translucent_fire(float t) {
        return vec4(0.3, 0.5, 0.7, t);
    }
    """)
