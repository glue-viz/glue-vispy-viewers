from matplotlib.colors import ListedColormap
from vispy.color import BaseColormap


def create_cmap_template(n):
    lines = [
        "vec4 translucent_colormap(float t) {",
    ]
    for i in range(n-1):
        lines.append(f"    if (t <= {(i+1) / n})")
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


def get_mpl_cmap(cmap):

    if isinstance(cmap, ListedColormap):
        colors = cmap.colors
        n_colors = len(colors)
        colors = [color + [index / n_colors] for index, color in enumerate(colors)]
    else:
        n_colors = 256
        colors = [cmap(index / n_colors)[:3] + (index / n_colors,) for index in range(n_colors)]

    template = create_cmap_template(n_colors)

    class MatplotlibCmap(BaseColormap):
        glsl_map = template

    return MatplotlibCmap(colors=colors)
