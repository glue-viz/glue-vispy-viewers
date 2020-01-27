import numpy as np
from scipy.ndimage import gaussian_filter

from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute

from .layer_state import IsosurfaceLayerState
from ..common.layer_artist import VispyLayerArtist

from vispy.color import BaseColormap

from .multi_iso_visual import MultiIsoVisual

DATA_PROPERTIES = set(['attribute', 'level_low', 'level_high'])
LEVEL_PROPERTIES = set(['step_value'])
COLOR_PROPERTIES = set(['color', 'alpha', 'cmap'])
STEP_PROPERTIES = set(['step'])


# TODO: create colormaps that is prettier
class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(int l){
    if (l==1)
        {return $color_0;}
    if (l==2)
        {return $color_1;}
    if (l==3)
        {return $color_2;}
    if (l==4)
        {return $color_3;}
    if (l==5)
        {return $color_4;}
    if (l==6)
        {return $color_5;}
    if (l==7)
        {return $color_6;}
    if (l==8)
        {return $color_7;}
    if (l==9)
        {return $color_8;}
    if (l==10)
        {return $color_9;}

    }
    """
# class AutoCmap(BaseColormap):
#     colors =
#     glsl_map = """
#     vec4 translucent_grays(int l){
#
#     }
#     """
# vec4 translucent_fire(float t) {
#         return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
#     }


class IsosurfaceLayerArtist(VispyLayerArtist):
    """
    A layer artist to render isosurfaces.
    """

    def __init__(self, vispy_viewer, layer=None, layer_state=None):

        super(IsosurfaceLayerArtist, self).__init__(layer)

        self._clip_limits = None

        self.layer = layer or layer_state.layer
        self.vispy_widget = vispy_viewer._vispy_widget

        # TODO: need to remove layers when layer artist is removed
        self._viewer_state = vispy_viewer.state
        self.state = layer_state or IsosurfaceLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        # self._iso_visual = scene.Isosurface(np.ones((3, 3, 3)), level=0.5, shading='smooth')
        # Create isosurface visual
        self._iso_visual = MultiIsoVisual(np.ones((3, 3, 3)), step=4, relative_step_size=0.5)
        # relative_step_size: ray casting performance, recommond 0.5~1.5)
        self.vispy_widget.add_data_visual(self._iso_visual)

        self._viewer_state.add_global_callback(self._update_volume)
        self.state.add_global_callback(self._update_volume)

        self.reset_cache()

    def reset_cache(self):
        self._last_viewer_state = {}
        self._last_layer_state = {}

    @property
    def bbox(self):
        return (-0.5, self.layer.shape[2] - 0.5,
                -0.5, self.layer.shape[1] - 0.5,
                -0.5, self.layer.shape[0] - 0.5)

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self.vispy_widget.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        self._iso_visual.parent = None

    def _update_level(self):
        # TODO: set iso clim
        # self._iso_visual.set_data()
        pass

    def _update_step(self):
        # TODO: generate a new color and transparancy scheme based on step num
        self._iso_visual.step = self.state.step
        self.redraw()
        # self._update_color()

    def _update_color(self):
        cmap_data = self.state.cmap(np.linspace(0, 1, 10).tolist())  # self.cmap returns 10 colors
        cmap_data = cmap_data.tolist()
        t = TransFire(colors=cmap_data)
        self._iso_visual.cmap = t
        self.redraw()

    def _update_data(self):

        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                mask = np.zeros(self.layer.data.shape, dtype=bool)
            data = mask.astype(float)
        else:
            data = self.layer[self.state.attribute]

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
        gaussian_data = gaussian_filter(data/4, 1)

        # TODO: the clim here conflict with set levels
        # self._iso_visual.set_data(
        # np.nan_to_num(gaussian_data),
        # clim=(self.level_low, self.level_high))
        # self._iso_visual.step = self.step

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

    def _update_volume(self, force=False, **kwargs):

        if self.state.attribute is None or self.state.layer is None:
            return

        # Figure out which attributes are different from before. Ideally we shouldn't
        # need this but currently this method is called multiple times if an
        # attribute is changed due to x_att changing then hist_x_min, hist_x_max, etc.
        # If we can solve this so that _update_histogram is really only called once
        # then we could consider simplifying this. Until then, we manually keep track
        # of which properties have changed.

        changed = set()

        if not force:

            for key, value in self._viewer_state.as_dict().items():
                if value != self._last_viewer_state.get(key, None):
                    changed.add(key)

            for key, value in self.state.as_dict().items():
                if value != self._last_layer_state.get(key, None):
                    changed.add(key)

        self._last_viewer_state.update(self._viewer_state.as_dict())
        self._last_layer_state.update(self.state.as_dict())

        if force or len(changed & DATA_PROPERTIES) > 0:
            self._update_data()

        if force or len(changed & LEVEL_PROPERTIES) > 0:
            self._update_level()

        if force or len(changed & COLOR_PROPERTIES) > 0:
            self._update_color()

        if force or len(changed & STEP_PROPERTIES) > 0:
            self._update_step()

    def update(self):
        self._update_volume(force=True)
        self.redraw()
