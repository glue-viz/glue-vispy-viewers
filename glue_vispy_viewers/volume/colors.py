from glue.config import AsinhStretch, LogStretch, SqrtStretch
from matplotlib.colors import ListedColormap
from vispy.color import BaseColormap


def create_cmap_template(n, stretch_glsl):
    ts = tuple((i + 1) / n for i in range(n-1))
    lines = [
        "vec4 translucent_colormap(float t) {",
        f"    float s = {stretch_glsl};"
    ]
    for i, t in enumerate(ts):
        lines.append(f"    if (s <= {t})")
        lines.append(f"        {{ return $color_{i}; }}")
    lines.append(f"    return $color_{n-1};")
    lines.append("}")

    return "\n".join(lines)


def glsl_for_stretch(stretch, param="t"):
    if isinstance(stretch, LogStretch):
        return f"log({stretch.a} * {param} + 1.0) / log({stretch.a} + 1.0)"
    elif isinstance(stretch, SqrtStretch):
        return f"sqrt({param})"
    elif isinstance(stretch, AsinhStretch):
        reciprocal = 1 / stretch.a
        param_rec = f"{param} * {reciprocal}"
        return f"log({param_rec} + sqrt(pow({param_rec}, 2) + 1)) / log({reciprocal} + sqrt(pow({reciprocal}, 2) + 1))"
    return param


def get_translucent_cmap(r, g, b, stretch):

    func = glsl_for_stretch(stretch)

    class TranslucentCmap(BaseColormap):
        glsl_map = """
        vec4 translucent_fire(float t) {{
            return vec4({0}, {1}, {2}, {3});
        }}
        """.format(r, g, b, func)

    return TranslucentCmap()


def get_mpl_cmap(cmap, stretch):

    if isinstance(cmap, ListedColormap):
        colors = cmap.colors
        n_colors = len(colors)
        ts = stretch([index / n_colors for index in range(len(colors))])
        colors = [color + [t] for t, color in zip(ts, colors)]
    else:
        n_colors = 256
        ts = stretch([index / n_colors for index in range(n_colors)])
        colors = [cmap(t)[:3] + (t,) for t in ts]

    stretch_glsl = glsl_for_stretch(stretch)
    template = create_cmap_template(n_colors, stretch_glsl)

    class MatplotlibCmap(BaseColormap):
        glsl_map = template
    
    return MatplotlibCmap(colors=colors)
