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


from ..extern.vispy.color import BaseColormap, get_colormaps
from ..extern.vispy.visuals.volume import frag_dict, FRAG_SHADER

from itertools import cycle
from .multi_iso_visual import MultiIsoVisual

# TODO: create colormaps that is prettier
class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class IsosurfaceLayerArtist(LayerArtistBase):
    """
    A layer artist to render isosurfaces.
    """

    attribute = CallbackProperty()
    level_low = CallbackProperty()
    level_high = CallbackProperty()
    color = CallbackProperty()
    # alpha = CallbackProperty()
    step = CallbackProperty()
    step_value = CallbackProperty()

    def __init__(self, layer, vispy_viewer):

        super(IsosurfaceLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer

        # self._iso_visual = scene.Isosurface(np.ones((3, 3, 3)), level=0.5, shading='smooth')
        # Create isosurface visual
        self._iso_visual = MultiIsoVisual(np.ones((3, 3, 3)), step=4, relative_step_size=0.5)
        # relative_step_size: ray casting performance, recommond 0.5~1.5)
        self.vispy_viewer.add_data_visual(self._iso_visual)
        self._vispy_color = None

        # Set up connections so that when any of the properties are
        # modified, we update the appropriate part of the visualization
        add_callback(self, 'attribute', nonpartial(self._update_data))
        add_callback(self, 'level_low', nonpartial(self._update_data))
        add_callback(self, 'level_high', nonpartial(self._update_data))
        add_callback(self, 'color', nonpartial(self._update_color))
        # add_callback(self, 'alpha', nonpartial(self._update_color))
        add_callback(self, 'step', nonpartial(self._update_step))
        add_callback(self, 'step_value', nonpartial(self._update_level))

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
        if self.level_high and self.level_low and self.step:
            # TODO: also the clim should be changed according to high and low?
            # self._iso_visual.threshold = np.mean(self.layer.data)
            print('layer.data', self.layer.data['PRIMARY'])
            self._iso_visual.step = self.step
            print('set level', self.step)
            print('threshold', self.level_high)
            self.redraw()

    def _update_step(self):
        # TODO: generate a new color and transparancy scheme based on step num
        self._update_level()

    def _update_color(self):
        self._update_vispy_color()
        if self._vispy_color is not None:
            self._iso_visual.color = self._vispy_color
        # TODO: check if new color scheme works
        self._iso_visual.cmap = TransFire()
        # TODO: toggle color map code in volume.py
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

        self._iso_visual.set_data(np.nan_to_num(gaussian_data))
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
