from __future__ import absolute_import, division, print_function

import sys
import uuid

import numpy as np
from matplotlib.colors import ColorConverter

from glue.external.echo import CallbackProperty, add_callback
from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase
from glue.utils import nonpartial
from glue.core.exceptions import IncompatibleAttribute
from .volume_visual import MultiVolume
from .colors import get_translucent_cmap


class VolumeLayerArtist(LayerArtistBase):
    """
    A layer artist to render volumes.

    This is more complex than for other visual types, because for volumes, we
    need to manage all the volumes via a single MultiVolume visual class for
    each data viewer.
    """

    attribute = CallbackProperty()
    vmin = CallbackProperty()
    vmax = CallbackProperty()
    color = CallbackProperty()
    cmap = CallbackProperty()
    alpha = CallbackProperty()
    subset_mode = CallbackProperty()

    def __init__(self, layer, vispy_viewer=None):

        super(VolumeLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer
        self.vispy_widget = vispy_viewer._vispy_widget

        # We create a unique ID for this layer artist, that will be used to
        # refer to the layer artist in the MultiVolume. We have to do this
        # rather than use self.id because we can't guarantee the latter is
        # unique.
        self.id = str(uuid.uuid4())

        # We need to use MultiVolume instance to store volumes, but we should
        # only have one per canvas. Therefore, we store the MultiVolume
        # instance in the vispy viewer instance.
        if not hasattr(self.vispy_widget, '_multivol'):

            # Set whether we are emulating a 3D texture. This needs to be
            # enabled as a workaround on Windows otherwise VisPy crashes.
            emulate_texture = (sys.platform == 'win32' and
                               sys.version_info[0] < 3)

            multivol = MultiVolume(threshold=0.1, emulate_texture=emulate_texture)

            self.vispy_widget.add_data_visual(multivol)
            self.vispy_widget._multivol = multivol

        self._multivol = self.vispy_widget._multivol
        self._multivol.allocate(self.id)

        # Set up connections so that when any of the properties are
        # modified, we update the appropriate part of the visualization
        add_callback(self, 'attribute', nonpartial(self._update_data))
        add_callback(self, 'vmin', nonpartial(self._update_limits))
        add_callback(self, 'vmax', nonpartial(self._update_limits))
        add_callback(self, 'color', nonpartial(self._update_cmap_from_color))
        add_callback(self, 'cmap', nonpartial(self._update_cmap))
        add_callback(self, 'alpha', nonpartial(self._update_alpha))
        if isinstance(self.layer, Subset):
            add_callback(self, 'subset_mode', nonpartial(self._update_data))

        self._clip_limits = None

    @property
    def visual(self):
        return self._multivol

    @property
    def bbox(self):
        return (-0.5, self.layer.shape[2] - 0.5,
                -0.5, self.layer.shape[1] - 0.5,
                -0.5, self.layer.shape[0] - 0.5)

    @property
    def shape(self):
        return self.layer.shape

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
        self.vispy_widget.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        # We don't want to deallocate here because this can be called if we
        # disable the layer due to incompatible attributes
        self._multivol.set_data(self.id, np.zeros(self._multivol._data_shape))

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def _update_cmap_from_color(self):
        cmap = get_translucent_cmap(*ColorConverter().to_rgb(self.color))
        self._multivol.set_cmap(self.id, cmap)
        self.redraw()

    def _update_cmap(self):
        self._multivol.set_cmap(self.id, self.cmap)
        self.redraw()

    def _update_limits(self):
        self._multivol.set_clim(self.id, (self.vmin, self.vmax))
        self.redraw()

    def _update_alpha(self):
        self._multivol.set_weight(self.id, self.alpha)
        self.redraw()

    def _update_data(self):

        if isinstance(self.layer, Subset):

            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self._enabled = True

            if self.subset_mode == 'outline':
                data = mask.astype(float)
            else:
                data = self.layer.data[self.attribute] * mask
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

        self._multivol.set_data(self.id, data)
        self.redraw()

    def _update_visibility(self):
        if self.visible:
            self._multivol.enable(self.id)
        else:
            self._multivol.disable(self.id)
        self.redraw()

    def set_coordinates(self, x_coord, y_coord, z_coord):
        pass

    def set(self, **kwargs):

        # This method can be used to set many properties in one go, and will
        # make sure that the order is correct.

        def priorities(value):
            if 'attribute' in value:
                return 0
            elif 'mode' in value:
                return 1
            else:
                return 2

        for attr in sorted(kwargs, key=priorities):
            setattr(self, attr, kwargs[attr])

    def set_clip(self, limits):
        self._clip_limits = limits
        self._update_data()
