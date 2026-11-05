import numpy as np
from glue.config import AsinhStretch, LinearStretch, LogStretch, SqrtStretch, DictRegistry
from matplotlib.colors import ListedColormap
from vispy.color import BaseColormap, ColorArray
from vispy.color.colormap import LUT_len
from uuid import uuid4


class GLSLStretchRegistry(DictRegistry):

    def add(self, stretch_cls, glsl):
        self.members[stretch_cls] = glsl


stretch_glsl = GLSLStretchRegistry()
stretch_glsl.add(LogStretch, "log({stretch.a} * {parameter} + 1.0) / log({stretch.a} + 1.0)")
stretch_glsl.add(SqrtStretch, "sqrt({parameter})")
stretch_glsl.add(AsinhStretch,
                 "log({parameter} / {stretch.a} + sqrt(pow({parameter} / {stretch.a}, 2) + 1)) / "
                 "log(1.0 / {stretch.a} + sqrt(pow(1.0 / {stretch.a}, 2) + 1))")
stretch_glsl.add(LinearStretch, "{parameter}")


def glsl_for_stretch(stretch, parameter="t"):
    template = stretch_glsl.members.get(type(stretch), "{param}")
    return template.format(stretch=stretch, parameter=parameter)


# This is based on `vispy.color.colormap.Colormap`
# In a similar vein to how we needed to create our own MultiVolumeVisual class,
# the primary issue with the VisPy Colormap class is that the colormap shader
# creates a particular name for the sampler uniform, but we need a separate
# sampler for each layer
class CustomColormap(BaseColormap):

    def __init__(self, colors, controls=None, *,
                 bad_color=None, low_color=None, high_color=None):

        ncontrols = len(colors)
        if controls is None:
            controls = np.linspace(0.0, 1.0, ncontrols)
        assert len(controls) == ncontrols
        self._controls = np.array(controls, dtype=np.float32)

        c_rgba = ColorArray(colors).rgba
        self.texture_map_data = np.zeros((LUT_len, 1, 4), dtype=np.float32)
        texture_len = self.texture_map_data.shape[0]
        x = np.linspace(0.0, 1.0, texture_len)
        self.texture_map_data[:, 0, 0] = np.interp(x, controls, c_rgba[:, 0])
        self.texture_map_data[:, 0, 1] = np.interp(x, controls, c_rgba[:, 1])
        self.texture_map_data[:, 0, 2] = np.interp(x, controls, c_rgba[:, 2])
        self.texture_map_data[:, 0, 3] = np.interp(x, controls, c_rgba[:, 3])

        self.uuid = uuid4().hex
        self.texture_name = f"texture2D_LUT_{self.uuid}"
        self.glsl_map = f"""
        uniform sampler2D {self.texture_name};
        vec4 colormap(float t) {{
            return texture2D({self.texture_name}, vec2(0.0, clamp(t, 0.0, 1.0)));
        }}
        """

        super().__init__(colors, bad_color=bad_color,
                         high_color=high_color, low_color=low_color)

    def texture_lut(self):
        return self.texture_map_data


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
        ts = stretch([index / (n_colors - 1) for index in range(n_colors)])
        colors = [[*color, t] for t, color in zip(ts, colors)]
    else:
        n_colors = 256
        ts = stretch([index / (n_colors - 1) for index in range(n_colors)])
        colors = [[*cmap(t)[:3], t] for t in ts]

    return CustomColormap(colors=colors, controls=ts)
