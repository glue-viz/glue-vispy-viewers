import uuid

import numpy as np

from matplotlib.colors import ColorConverter

from glue.core.data import Subset, Data
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE
from glue.viewers3d.volume.data_proxy import DataProxy
from glue.viewers3d.volume.layer_state import VolumeLayerState

from .colors import get_mpl_cmap, get_translucent_cmap
from ..common.layer_artist import VispyLayerArtist


COLOR_PROPERTIES = set(['cmap', 'color', 'color_mode', 'stretch', 'stretch_parameters'])


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

        self._multivol = self.vispy_widget._multivol
        self._multivol.allocate(self.id)

        self._viewer_state.add_global_callback(self._update_volume)
        self.state.add_global_callback(self._update_volume)

        self.reset_cache()

        self._data_proxy = None

    def reset_cache(self):
        self._last_viewer_state = {}
        self._last_layer_state = {}

    @property
    def visual(self):
        return self._multivol

    @property
    def bbox(self):
        return (-0.5, self.layer.shape[self._viewer_state.x_att.axis] - 0.5,
                -0.5, self.layer.shape[self._viewer_state.y_att.axis] - 0.5,
                -0.5, self.layer.shape[self._viewer_state.z_att.axis] - 0.5)

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
        self._multivol.disable(self.id)

    def remove(self):
        """
        Remove the layer artist for good
        """
        self._multivol.deallocate(self.id)
        ARRAY_CACHE.pop(self.id, None)
        PIXEL_CACHE.pop(self.id, None)

    def _update_cmap(self):
        if self.state.color_mode == "Fixed":
            cmap = get_translucent_cmap(*ColorConverter().to_rgb(self.state.color),
                                        self.state.stretch_object)
        else:
            cmap = get_mpl_cmap(self.state.cmap, self.state.stretch_object)

        self._multivol.set_cmap(self.id, cmap)
        self.redraw()

    def _update_limits(self):
        if isinstance(self.layer, Subset):
            self._multivol.set_clim(self.id, None)
        else:
            self._multivol.set_clim(self.id, (self.state.vmin, self.state.vmax))
        self.redraw()

    def _update_alpha(self):
        self._multivol.set_weight(self.id, self.state.alpha)
        self.redraw()

    def _update_subset_mode(self):
        if isinstance(self.state.layer, Data) or self.state.subset_mode == 'outline':
            self._multivol.set_multiply(self.id, None)
        else:
            label = self._multivol.label_for_layer(self.state.layer.data)
            self._multivol.set_multiply(self.id, label)
        self.redraw()

    def _update_data(self):

        if self._data_proxy is None:
            self._data_proxy = DataProxy(self._viewer_state, self)
            self._multivol.set_data(self.id, self._data_proxy, layer=self.layer)
        else:
            self._multivol._update_scaled_data(self.id)

        self._update_subset_mode()

    def _update_visibility(self):
        if self.state.visible:
            self._multivol.enable(self.id)
        else:
            self._multivol.disable(self.id)
        self.redraw()

    def set_clip(self, limits):
        pass

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

        if force or len(changed & COLOR_PROPERTIES) > 0:
            self._update_cmap()

        if force or 'vmin' in changed or 'vmax' in changed:
            self._update_limits()

        if force or 'alpha' in changed:
            self._update_alpha()

        # TODO: Feel like we shouldn't need the axis atts here
        if force or any(att in changed for att in
                        ('layer', 'attribute', 'slices', 'x_att', 'y_att', 'z_att')):
            self._update_data()

        if force or 'subset_mode' in changed:
            self._update_subset_mode()

        if force or 'visible' in changed:
            self._update_visibility()

    def update(self):
        self._update_volume(force=True)
        self.redraw()
