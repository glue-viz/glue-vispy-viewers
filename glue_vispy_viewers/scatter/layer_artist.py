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

        self._size = 10
        self._color = (1, 1, 1)
        self._alpha = 1.
        self._color_data = None
        self._size_data = None

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
        self._scat_visual.parent = None

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def set_size(self, size=None, attribute=None, vmin=None, vmax=None, scaling=None):
        self._size = size
        self._size_attribute = attribute
        self._size_vmin = vmin
        self._size_vmax = vmax
        self._size_scaling = scaling
        self._update_size_data()
        self._update_data()

    def _update_size_data(self):
        if self._size is None:
            data = self.layer[self._size_attribute]
            size = np.abs(np.nan_to_num(data))
            size = 20 * (size - self._size_vmin) / (self._size_vmax - self._size_vmin)
            self._size_data = size * self._size_scaling
        else:
            self._size_data = self._size

    def set_color(self, color=None, attribute=None, vmin=None, vmax=None, cmap=None):
        self._color = color
        self._color_attribute = attribute
        self._color_vmin = vmin
        self._color_vmax = vmax
        self._color_cmap = cmap
        self._update_color_data()
        self._update_data()

    def _update_color_data(self):
        if self._color is None:
            data = self.layer[self._size_attribute]
            # TODO: implement colormap support
        else:
            self._color_data = np.ones((self.n_points, 4), dtype=np.float32)
            self._color_data[:, 0] = self._color[0]
            self._color_data[:, 1] = self._color[1]
            self._color_data[:, 2] = self._color[2]
            self._color_data[:, 3] = self._alpha

    def set_alpha(self, alpha):
        self._alpha = alpha
        self._update_color_data()
        self._update_data()

    @property
    def n_points(self):
        return self.layer.shape[0]

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
        if self._color_data is None:
            self._update_color_data()
        if self._size_data is None:
            self._update_size_data()
        self._scat_visual.set_data(self._marker_data,
                                   edge_color=None, face_color=self._color_data,
                                   size=self._size_data)
        self.redraw()

    @property
    def default_limits(self):
        if self._marker_data is None:
            raise ValueError("Data not yet set")
        dmin = np.nanmin(self._marker_data,axis=0)
        dmax = np.nanmax(self._marker_data,axis=0)
        # TODO: the following can be optimized
        return tuple(np.array([dmin, dmax]).transpose().ravel())

    def _update_visibility(self):
        if self.visible:
            self._scat_visual.parent = self.vispy_viewer.view.scene
        else:
            self._scat_visual.parent = None
        self.redraw()
