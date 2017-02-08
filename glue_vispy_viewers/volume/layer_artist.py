from __future__ import absolute_import, division, print_function

import sys
import uuid

import numpy as np
from matplotlib.colors import ColorConverter

from glue.core.data import Subset
from glue.config import settings
from glue.core.exceptions import IncompatibleAttribute
from .volume_visual import MultiVolume
from .colors import get_translucent_cmap
from .layer_state import VolumeLayerState
from ..common.layer_artist import VispyLayerArtist


class VolumeLayerArtist(VispyLayerArtist):
    """
    A layer artist to render volumes.

    This is more complex than for other visual types, because for volumes, we
    need to manage all the volumes via a single MultiVolume visual class for
    each data viewer.
    """

    def __init__(self, vispy_viewer=None, layer=None, layer_state=None):

        super(VolumeLayerArtist, self).__init__(layer)

        self._clip_limits = None

        self.layer = layer or layer_state.layer
        self.vispy_viewer = vispy_viewer
        self.vispy_widget = vispy_viewer._vispy_widget

        # TODO: need to remove layers when layer artist is removed
        self._viewer_state = vispy_viewer.state
        self.state = layer_state or VolumeLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

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

            multivol = MultiVolume(threshold=0.1, emulate_texture=emulate_texture,
                                   bgcolor=settings.BACKGROUND_COLOR)

            self.vispy_widget.add_data_visual(multivol)
            self.vispy_widget._multivol = multivol

        self._multivol = self.vispy_widget._multivol
        self._multivol.allocate(self.id)

        # TODO: Maybe should reintroduce global callbacks since they behave differently...
        self.state.add_callback('*', self._update_from_state, as_kwargs=True)
        self._update_from_state(**self.state.as_dict())

        self.visible = True

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

    def _update_from_state(self, **props):

        if 'color' in props:
            self._update_cmap_from_color()

        if 'vmin' in props or 'vmax' in props:
            self._update_limits()

        if 'alpha' in props:
            self._update_alpha()

        if 'attribute' in props or 'subset_mode' in props:
            self._update_data()

    def _update_cmap_from_color(self):
        cmap = get_translucent_cmap(*ColorConverter().to_rgb(self.state.color))
        self._multivol.set_cmap(self.id, cmap)
        self.redraw()

    def _update_limits(self):
        self._multivol.set_clim(self.id, (self.state.vmin, self.state.vmax))
        self.redraw()

    def _update_alpha(self):
        self._multivol.set_weight(self.id, self.state.alpha)
        self.redraw()

    def _update_data(self):

        if self.state.attribute is None:
            return

        if isinstance(self.layer, Subset):

            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self._enabled = True

            if self.state.subset_mode == 'outline':
                data = mask.astype(float)
            else:
                data = self.layer.data[self.state.attribute] * mask
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

        self._multivol.set_data(self.id, data)
        self.redraw()

    def _update_visibility(self):
        if self.visible:
            self._multivol.enable(self.id)
        else:
            self._multivol.disable(self.id)
        self.redraw()

    def set_clip(self, limits):
        self._clip_limits = limits
        self._update_data()
