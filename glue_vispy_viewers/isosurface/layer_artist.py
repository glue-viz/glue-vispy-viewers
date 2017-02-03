from __future__ import absolute_import, division, print_function

import numpy as np
from matplotlib.colors import ColorConverter

from ..extern.vispy import scene
from ..extern.vispy.color import Color

from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute

from .layer_state import IsosurfaceLayerState
from ..common.layer_artist import VispyLayerArtist


class IsosurfaceLayerArtist(VispyLayerArtist):
    """
    A layer artist to render isosurfaces.
    """

    def __init__(self, vispy_viewer, layer=None, layer_state=None):

        super(IsosurfaceLayerArtist, self).__init__(layer)

        self._clip_limits = None

        self.layer = layer or layer_state.layer
        self.vispy_viewer = vispy_viewer
        self.vispy_widget = vispy_viewer._vispy_widget

        # TODO: need to remove layers when layer artist is removed
        self.viewer_state = vispy_viewer.viewer_state
        self.layer_state = layer_state or IsosurfaceLayerState(layer=self.layer)
        if self.layer_state not in self.viewer_state.layers:
            self.viewer_state.layers.append(self.layer_state)

        self._iso_visual = scene.Isosurface(np.ones((3, 3, 3)), level=0.5, shading='smooth')
        self.vispy_widget.add_data_visual(self._iso_visual)
        self._vispy_color = None

        # TODO: Maybe should reintroduce global callbacks since they behave differently...
        self.layer_state.add_callback('*', self._update_from_state, as_kwargs=True)
        self._update_from_state(**self.layer_state.as_dict())

        self.visible = True

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

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def _update_from_state(self, **props):
        if 'attribute' in props:
            self._update_data()
        if 'level' in props:
            self._update_level()
        if any(prop in props for prop in ('color', 'alpha')):
            self._update_color()

    def _update_level(self):
        self._iso_visual.level = self.layer_state.level
        self.redraw()

    def _update_color(self):
        self._update_vispy_color()
        if self._vispy_color is not None:
            self._iso_visual.color = self._vispy_color
        self.redraw()

    def _update_vispy_color(self):
        if self.layer_state.color is None:
            return
        self._vispy_color = Color(ColorConverter().to_rgb(self.layer_state.color))
        self._vispy_color.alpha = self.layer_state.alpha

    def _update_data(self):

        if self.layer_state.attribute is None:
            return

        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                mask = np.zeros(self.layer.data.shape, dtype=bool)
            data = mask.astype(float)
        else:
            data = self.layer[self.layer_state.attribute]

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

        self._iso_visual.set_data(np.nan_to_num(data).transpose())
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
