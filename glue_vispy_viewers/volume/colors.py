from matplotlib import colormaps
from vispy.color import BaseColormap


def create_cmap_template(n):
    lines = [
        "vec4 translucent_colormap(float t) {",
    ]
    for i in range(n-1):
        lines.append(f"    if (t < {i / n})")
        lines.append(f"        {{ return $color_{i}; }}")
    lines.append(f"    return $color_{n-1};")
    lines.append("}")

    return "\n".join(lines)


def get_translucent_cmap(r, g, b):

    class TranslucentCmap(BaseColormap):
        glsl_map = """
        vec4 translucent_fire(float t) {{
            return vec4({0}, {1}, {2}, t);
        }}
        """.format(r, g, b)

    return TranslucentCmap()


def get_linear_cmap(cl, ch):

    class LinearCmap(BaseColormap):
        c = tuple(f"{l} + t * ({h} - {l})" for l, h in zip(cl, ch))
        glsl_map = """
        vec4 translucent_linear(float t) {{
            return vec4({0}, {1}, {2}, t);
        }}
        """.format(*c)

    return LinearCmap()


def get_mpl_cmap(cmap_name):
    
    cmap = colormaps[cmap_name]
    colors = cmap.colors
    n_colors = len(colors)
    colors = [color + [index / n_colors] for index, color in enumerate(colors)]
    template = create_cmap_template(n_colors)
    print(template)

    class MatplotlibCmap(BaseColormap):
        glsl_map = template
        # glsl_map = """
        # vec4 test(float t) {
        #     if (t < 0.5) { return $color_0; }
        #     return $color_200;
        # }
        # """

    return MatplotlibCmap(colors=colors)


