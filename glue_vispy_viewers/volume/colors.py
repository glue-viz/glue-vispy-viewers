from vispy.color import BaseColormap


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
        vec4 translucent_fire(float t) {{
            return vec4({0}, {1}, {2}, t);
        }}
        """.format(*c)

    return LinearCmap()

