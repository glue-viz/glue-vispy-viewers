from __future__ import absolute_import, division, print_function

import numpy as np

from vispy import scene
from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase

class ScatterLayerArtist(LayerArtistBase):
    """
    A layer artist to render 3d scatter plots.
    """

    def __init__(self, layer, vispy_viewer):

        super(ScatterLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer
        self._scat_visual = scene.visuals.Markers()
        self.vispy_viewer.add_data_visual(self._scat_visual)
        self._marker_data = None

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        # self._update_visibility()

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self.vispy_viewer.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        self._scat_visual.parent = None

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    # def set_cmap(self, cmap):
    #     self._multivol.set_cmap(self.layer.label, cmap)
    #     self.redraw()
    #
    # def set_clim(self, clim):
    #     self._multivol.set_clim(self.layer.label, clim)
    #     self.redraw()
    #
    # def set_alpha(self, alpha):
    #     self._multivol.set_weight(self.layer.label, alpha)
    #     self.redraw()

    def set_coordinates(self, x_coord, y_coord, z_coord):
        self._x_coord = x_coord
        self._y_coord = y_coord
        self._z_coord = z_coord
        self._update_data()

    def _update_data(self):
        x = self.layer[self._x_coord]
        y = self.layer[self._y_coord]
        z = self.layer[self._z_coord]
        # TODO: avoid re-allocating an array every time
        self._marker_data = np.array([x, y, z]).transpose()
        self._scat_visual.set_data(self._marker_data)
        self.redraw()

    @property
    def default_limits(self):
        if self._marker_data is None:
            raise ValueError("Data not yet set")
        dmin = np.nanmin(self._marker_data,axis=0)
        dmax = np.nanmax(self._marker_data,axis=0)
        # TODO: the following can be optimized
        return tuple(np.array([dmin, dmax]).transpose().ravel())

    # def _update_visibility(self):
    #     if self.visible:
    #         self._multivol.enable(self.layer.label)
    #     else:
    #         self._multivol.disable(self.layer.label)
    #     self.redraw()
