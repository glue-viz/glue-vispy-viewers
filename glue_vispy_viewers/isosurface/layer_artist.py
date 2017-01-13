from __future__ import absolute_import, division, print_function

import numpy as np
from matplotlib.colors import ColorConverter
from scipy.ndimage import gaussian_filter
import os

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


# COLOR_BREWER = None
BREWER_COLOR_FILE = os.path.join(os.path.dirname(__file__), 'ColorBrewer_all_schemes_RGBonly3.XLS')


# TODO: add parameters of cmap and level from IsosurfaceLayerArtist
def set_brewer_color():
    import pandas as pd

    xl = pd.ExcelFile(BREWER_COLOR_FILE)
    df = xl.parse('Sheet1')[:1690]

    # TODO: 4.0 here will be replaced by level, 'Blues' will be replaced by chosen color in dropdown list
    # select specific data series upon UI setting
    mask = df['ColorName'].isin(['Blues']) & df['NumOfColors'].isin([4.0]) & df['Type'].isin(['seq'])
    sel = df[mask]
    print('sel', sel)
    index = sel.index[0] # int
    df_rgb = df.loc[range(index, index+int(4.0), 1)]

    # get color array
    color = np.ones((int(4.0), 4))
    color[:, 0] = np.array(df_rgb['R'])
    color[:, 1] = np.array(df_rgb['G'])
    color[:, 2] = np.array(df_rgb['B'])
    color[:, 3] = 255.0
    color /= 255.
    return color.tolist()


class Brewer(BaseColormap):
    colors = set_brewer_color()

    # Use $color_0 to refer to the first color in `colors`, and so on. These are vec4 vectors.
    glsl_map = """
    vec4 translucent_grays(int l) {
        if (l == 1)
            {return $color_0;}
        if (l == 2)
            {return $color_1;}
        if (l == 3)
            {return $color_2;}
        if (l == 4)
            {return $color_3;}
    }
    """


# original 'random' cmap, also need to change shader in_loop
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

        # Create isosurface visual
        # step is the level in shader as in self.shared_program['level'] = step
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
        add_callback(self, 'step', nonpartial(self._update_level()))
        add_callback(self, 'step_value', nonpartial(self._update_level))

        self._clip_limits = None
        print('step in init', self.step)

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

            # assign UI step to iso_visual
            self._iso_visual.step = self.step  # num of layers in isosurface
            self._update_color()

    def _update_color(self):
        self._update_vispy_color()
        # if self._vispy_color is not None:
        #     self._iso_visual.color = self._vispy_color

        # self._iso_visual.cmap = TransFire()
        print('self.step', self.step)
        self._iso_visual.cmap = Brewer()
        # TODO: toggle color map code in volume.py
        self.redraw()

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


