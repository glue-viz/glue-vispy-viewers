from __future__ import absolute_import, division, print_function
from vispy.color import BaseColormap

# create colormaps that work well for translucent and additive volume rendering
class TransFire(BaseColormap):
    glsl_map = """
        vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
        }
        """

class TransGrays(BaseColormap):
    glsl_map = """
        vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
        }
        """