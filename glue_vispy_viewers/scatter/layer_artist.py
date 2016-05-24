from __future__ import absolute_import, division, print_function

import uuid

import numpy as np

from glue.external.echo import CallbackProperty, add_callback

from glue.core.layer_artist import LayerArtistBase
from glue.utils import nonpartial
from glue.core.exceptions import IncompatibleAttribute

from .multi_scatter import MultiColorScatter


class ScatterLayerArtist(LayerArtistBase):
    """
    A layer artist to render 3d scatter plots.
    """

    _properties = ["size_mode", "size", "size_attribute", "size_vmin",
                   "size_vmax", "size_scaling", "color_mode", "color",
                   "cmap_attribute", "cmap_vmin", "cmap_vmax", "cmap",
                   "alpha", "layer"]

    size_mode = CallbackProperty(None)
    size = CallbackProperty()
    size_attribute = CallbackProperty()
    size_vmin = CallbackProperty()
    size_vmax = CallbackProperty()
    size_scaling = CallbackProperty()

    color_mode = CallbackProperty(None)
    color = CallbackProperty()
    cmap_attribute = CallbackProperty()
    cmap_vmin = CallbackProperty()
    cmap_vmax = CallbackProperty()
    cmap = CallbackProperty()
    alpha = CallbackProperty()

    def __init__(self, layer, vispy_viewer):

        super(ScatterLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer
        self.vispy_widget = vispy_viewer._vispy_widget

        # We create a unique ID for this layer artist, that will be used to
        # refer to the layer artist in the MultiColorScatter. We have to do this
        # rather than use self.id because we can't guarantee the latter is
        # unique.
        self.id = str(uuid.uuid4())

        # We need to use MultiColorScatter instance to store scatter plots, but
        # we should only have one per canvas. Therefore, we store the
        # MultiColorScatter instance in the vispy viewer instance.
        if not hasattr(self.vispy_widget, '_multiscat'):
            multiscat = MultiColorScatter()
            multiscat.set_gl_state(depth_test=False,
                                   blend=True,
                                   blend_func=('src_alpha', 'one_minus_src_alpha'))

            self.vispy_widget.add_data_visual(multiscat)
            self.vispy_widget._multiscat = multiscat

        self._multiscat = self.vispy_widget._multiscat
        self._multiscat.allocate(self.id)
        self._multiscat.set_zorder(self.id, self.get_zorder)

        # Set up connections so that when any of the size properties are
        # modified, we update the marker sizes
        add_callback(self, 'size_mode', nonpartial(self._update_sizes))
        add_callback(self, 'size', nonpartial(self._update_sizes))
        add_callback(self, 'size_attribute', nonpartial(self._update_sizes))
        add_callback(self, 'size_vmin', nonpartial(self._update_sizes))
        add_callback(self, 'size_vmax', nonpartial(self._update_sizes))
        add_callback(self, 'size_scaling', nonpartial(self._update_sizes))

        # Set up connections so that when any of the color properties are
        # modified, we update the marker colors
        add_callback(self, 'color_mode', nonpartial(self._update_colors))
        add_callback(self, 'color', nonpartial(self._update_colors))
        add_callback(self, 'cmap_attribute', nonpartial(self._update_colors))
        add_callback(self, 'cmap_vmin', nonpartial(self._update_colors))
        add_callback(self, 'cmap_vmax', nonpartial(self._update_colors))
        add_callback(self, 'cmap', nonpartial(self._update_colors))
        add_callback(self, 'alpha', nonpartial(self._update_alpha))

        # Set data caches
        self._marker_data = None
        self._color_data = None
        self._size_data = None

    @property
    def visual(self):
        return self._multiscat

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._multiscat.set_visible(self.id, self.visible)
        self.redraw()

    def get_zorder(self):
        return self.zorder

    @property
    def zorder(self):
        return self._zorder

    @zorder.setter
    def zorder(self, value):
        self._zorder = value
        self.redraw()

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self._multiscat._update()
        self.vispy_widget.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        self._multiscat.set_data_values(self.id, [], [], [])

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def _update_sizes(self):
        if self.size_mode is None:
            pass
        elif self.size_mode == 'fixed':
            self._multiscat.set_size(self.id, self.size * self.size_scaling)
        else:
            data = self.layer[self.size_attribute]
            size = np.abs(np.nan_to_num(data))
            size = 20 * (size - self.size_vmin) / (self.size_vmax - self.size_vmin)
            size_data = size * self.size_scaling
            self._multiscat.set_size(self.id, size_data)

    def _update_colors(self):
        if self.color_mode is None:
            pass
        elif self.color_mode == 'fixed':
            self._multiscat.set_color(self.id, self.color)
        else:
            data = self.layer[self.cmap_attribute]
            cmap_data = np.abs(np.nan_to_num(data))
            cmap_data = (cmap_data - self.cmap_vmin) / (self.cmap_vmax - self.cmap_vmin)
            cmap_data = self.cmap(cmap_data)
            self._multiscat.set_color(self.id, cmap_data)

    def _update_alpha(self):
        self._multiscat.set_alpha(self.id, self.alpha)

    def set_coordinates(self, x_coord, y_coord, z_coord):
        self._x_coord = x_coord
        self._y_coord = y_coord
        self._z_coord = z_coord
        self._update_data()

    def _update_data(self):

        try:
            x = self.layer[self._x_coord]
            y = self.layer[self._y_coord]
            z = self.layer[self._z_coord]
        except (IncompatibleAttribute, IndexError):
            # The following includes a call to self.clear()
            self.disable_invalid_attributes(self._x_coord, self._y_coord, self._z_coord)
            return
        else:
            self._enabled = True

        self._marker_data = np.array([x, y, z]).transpose()

        # We need to make sure we update the sizes and colors in case
        # these were set as arrays, since the size of the data might have
        # changed (in the case of subsets)

        with self._multiscat.delay_update():
            self._multiscat.set_data_values(self.id, x, y, z)
            self._update_sizes()
            self._update_colors()

        self.redraw()

    @property
    def default_limits(self):
        if self._marker_data is None:
            raise ValueError("Data not yet set")
        dmin = np.nanmin(self._marker_data, axis=0)
        dmax = np.nanmax(self._marker_data, axis=0)
        # TODO: the following can be optimized
        return tuple(np.array([dmin, dmax]).transpose().ravel())

    def __gluestate__(self, context):
        return dict((attr, context.id(getattr(self, attr))) for attr in self._properties)

    def set(self, **kwargs):

        # This method can be used to set many properties in one go, and will
        # make sure that the order is correct.

        def priorities(value):
            if 'mode' in value:
                return 0
            elif 'attribute' in value:
                return 1
            else:
                return 2

        for attr in sorted(kwargs, key=priorities):
            setattr(self, attr, kwargs[attr])
