from __future__ import absolute_import, division, print_function

import numpy as np
from matplotlib.colors import ColorConverter
from scipy.ndimage import gaussian_filter


from ..extern.vispy import scene
from ..extern.vispy.color import Color

from glue.external.echo import CallbackProperty, add_callback
from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase
from glue.utils import nonpartial
from glue.core.exceptions import IncompatibleAttribute


from ..extern.vispy.color import BaseColormap
from ..extern.vispy.visuals.volume import frag_dict, FRAG_SHADER

# Custom shader to replace existing iso one

ISO_SNIPPETS = dict(
    before_loop="""
        vec4 total_color = vec4(0.0);  // final color
        vec4 src = vec4(0.0);
        vec4 dst = vec4(0.0);
        vec3 dstep = 1.5 / u_shape;  // step to sample derivative
        gl_FragColor = vec4(0.0);
        float val_prev = 0;
        float outa = 0;
        vec3 loc_prev = vec3(0.0);
        vec3 loc_mid = vec3(0.0);
        float t1 = 0.6;
        float t2 = 0.4;

    """,
    in_loop="""
        if (val > t1 && val_prev < t1) {

            // Use bisection to find correct position of contour
            for (int i=0; i<20; i++) {
                loc_mid = 0.5 * (loc_prev + loc);
                val = $sample(u_volumetex, loc_mid).g;
                if (val > u_threshold) {
                    loc = loc_mid;
                } else {
                    loc_prev = loc_mid;
                }
            }

            dst = $cmap(val);
            dst = calculateColor(dst, loc, dstep);

            src = total_color;

            outa = src.a + dst.a * (1 - src.a);
            total_color = (src * src.a + dst * dst.a * (1 - src.a)) / outa;
            total_color.a = outa;
        }

        if (val < t1 && val_prev > t1) {

            // Use bisection to find correct position of contour
            for (int i=0; i<20; i++) {
                loc_mid = 0.5 * (loc_prev + loc);
                val = $sample(u_volumetex, loc_mid).g;
                if (val < u_threshold) {
                    loc = loc_mid;
                } else {
                    loc_prev = loc_mid;
                }
            }

            dst = $cmap(val);
            dst = calculateColor(dst, loc, dstep);

            src = total_color;

            outa = src.a + dst.a * (1 - src.a);
            total_color = (src * src.a + dst * dst.a * (1 - src.a)) / outa;
            total_color.a = outa;
        }

        if (val > t2 && val_prev < t2) {

            // Use bisection to find correct position of contour
            for (int i=0; i<20; i++) {
                loc_mid = 0.5 * (loc_prev + loc);
                val = $sample(u_volumetex, loc_mid).g;
                if (val > u_threshold) {
                    loc = loc_mid;
                } else {
                    loc_prev = loc_mid;
                }
            }

            dst = $cmap(val);
            dst = calculateColor(dst, loc, dstep);
            dst.a = 0.25;

            src = total_color;

            outa = src.a + dst.a * (1 - src.a);
            total_color = (src * src.a + dst * dst.a * (1 - src.a)) / outa;
            total_color.a = outa;

        }

        if (val < t2 && val_prev > t2) {

            // Use bisection to find correct position of contour
            for (int i=0; i<20; i++) {
                loc_mid = 0.5 * (loc_prev + loc);
                val = $sample(u_volumetex, loc_mid).g;
                if (val < u_threshold) {
                    loc = loc_mid;
                } else {
                    loc_prev = loc_mid;
                }
            }

            dst = $cmap(val);
            dst = calculateColor(dst, loc, dstep);
            dst.a = 0.25;

            src = total_color;

            outa = src.a + dst.a * (1 - src.a);
            total_color = (src * src.a + dst * dst.a * (1 - src.a)) / outa;
            total_color.a = outa;

        }

        val_prev = val;
        loc_prev = loc;
        """,
    after_loop="""
        gl_FragColor = total_color;
        """,
)

ISO_FRAG_SHADER = FRAG_SHADER.format(**ISO_SNIPPETS)

frag_dict['iso'] = ISO_FRAG_SHADER


class TwoLevel(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {{
        if(t > 0.5) {
            return vec4(0.3, 0.0, 0.6, 1.0);
        } else {
            return vec4(0.43, 0.09, 0.43, 0.5);
        }
    }}
    """


class IsosurfaceLayerArtist(LayerArtistBase):
    """
    A layer artist to render isosurfaces.
    """

    attribute = CallbackProperty()
    level = CallbackProperty()
    color = CallbackProperty()
    alpha = CallbackProperty()

    def __init__(self, layer, vispy_viewer):

        super(IsosurfaceLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer

        # self._iso_visual = scene.Isosurface(np.ones((3, 3, 3)), level=0.5, shading='smooth')
        # Create isosurface visual
        self._iso_visual = scene.visuals.Volume(np.ones((3, 3, 3)), method='iso', relative_step_size=0.5)
        # relative_step_size: ray casting performance, recommond 0.5~1.5)
        self.vispy_viewer.add_data_visual(self._iso_visual)
        self._vispy_color = None

        # Set up connections so that when any of the properties are
        # modified, we update the appropriate part of the visualization
        add_callback(self, 'attribute', nonpartial(self._update_data))
        add_callback(self, 'level', nonpartial(self._update_level))
        add_callback(self, 'color', nonpartial(self._update_color))
        add_callback(self, 'alpha', nonpartial(self._update_color))

        self._clip_limits = None

    @property
    def bbox(self):
        return (-0.5, self.layer.shape[2] - 0.5,
                -0.5, self.layer.shape[1] - 0.5,
                -0.5, self.layer.shape[0] - 0.5)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._update_visibility()

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self.vispy_viewer.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        self._iso_visual.parent = None

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def _update_level(self):
        self._iso_visual.threshold = self.level
        self.redraw()

    def _update_color(self):
        self._update_vispy_color()
        if self._vispy_color is not None:
            self._iso_visual.color = self._vispy_color
        # TODO: accept color from ui
        self._iso_visual.cmap = TwoLevel()
        # self._update_vispy_color()
        # self._iso_visual.color = self._vispy_color
        self.redraw()
        pass

    def _update_vispy_color(self):
        # TODO: add cmap that contains color numbers as same as isosurface shell number
        # if self.color is None:
        #     return
        # self._vispy_color = Color(ColorConverter().to_rgb(self.color))
        # self._vispy_color.alpha = self.alpha
        pass

    def _update_data(self):
        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                mask = np.zeros(self.layer.data.shape, dtype=bool)
            data = mask.astype(float)
        else:
            data = self.layer[self.attribute]

        if self._clip_limits is not None:
            xmin, xmax, ymin, ymax, zmin, zmax = self._clip_limits
            imin, imax = int(np.ceil(xmin)), int(np.ceil(xmax))
            jmin, jmax = int(np.ceil(ymin)), int(np.ceil(ymax))
            kmin, kmax = int(np.ceil(zmin)), int(np.ceil(zmax))
            invalid = -np.inf
            data = data.copy()
            data[:, :, :imin] = invalid
            data[:, :, imax:] = invalid
            data[:, :jmin] = invalid
            data[:, jmax:] = invalid
            data[:kmin] = invalid
            data[kmax:] = invalid

        # self._iso_visual.set_data(np.nan_to_num(data).transpose())
        # TODO: gaussian smooth for the data, why multiply by 4?
        gaussian_data = gaussian_filter(data/4, 1)

        self._iso_visual.set_data(np.nan_to_num(gaussian_data))  # or .transpose()?
        self.redraw()

    def _update_visibility(self):
        # if self.visible:
        #     self._iso_visual.parent =
        # else:
        #     self._multivol.disable(self.id)
        self.redraw()

    def set_clip(self, limits):
        self._clip_limits = limits
        self._update_data()
