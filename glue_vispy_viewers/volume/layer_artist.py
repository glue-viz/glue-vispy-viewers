import uuid
import weakref

import numpy as np

from matplotlib.colors import ColorConverter

from glue.core.data import Subset, Data
from glue.core.exceptions import IncompatibleAttribute
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE
from .colors import get_translucent_cmap
from .layer_state import VolumeLayerState
from ..common.layer_artist import VispyLayerArtist


class DataProxy(object):

    def __init__(self, viewer_state, layer_artist):
        self._viewer_state = weakref.ref(viewer_state)
        self._layer_artist = weakref.ref(layer_artist)

    @property
    def layer_artist(self):
        return self._layer_artist()

    @property
    def viewer_state(self):
        return self._viewer_state()

    @property
    def shape(self):

        x_axis = self.viewer_state.x_att.axis
        y_axis = self.viewer_state.y_att.axis
        z_axis = self.viewer_state.z_att.axis

        if isinstance(self.layer_artist.layer, Subset):
            full_shape = self.layer_artist.layer.data.shape
        else:
            full_shape = self.layer_artist.layer.shape

        return full_shape[z_axis], full_shape[y_axis], full_shape[x_axis]

    def compute_fixed_resolution_buffer(self, bounds=None):

        shape = [bound[2] for bound in bounds]

        if self.layer_artist is None or self.viewer_state is None:
            return np.broadcast_to(0, shape)

        if isinstance(self.layer_artist.layer, Subset):
            try:
                subset_state = self.layer_artist.layer.subset_state
                result = self.layer_artist.layer.data.compute_fixed_resolution_buffer(
                    target_data=self.layer_artist._viewer_state.reference_data,
                    bounds=bounds, subset_state=subset_state,
                    cache_id=self.layer_artist.id)
            except IncompatibleAttribute:
                self.layer_artist.disable_incompatible_subset()
                return np.broadcast_to(0, shape)
            else:
                self.layer_artist.enable()
        else:
            try:
                result = self.layer_artist.layer.compute_fixed_resolution_buffer(
                    target_data=self.layer_artist._viewer_state.reference_data,
                    bounds=bounds, target_cid=self.layer_artist.state.attribute,
                    cache_id=self.layer_artist.id)
            except IncompatibleAttribute:
                self.layer_artist.disable('Layer data is not fully linked to reference data')
                return np.broadcast_to(0, shape)
            else:
                self.layer_artist.enable()

        return result


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
        self._multivol.disable(self.id)

    def remove(self):
        """
        Remove the layer artist for good
        """
        self._multivol.deallocate(self.id)
        ARRAY_CACHE.pop(self.id, None)
        PIXEL_CACHE.pop(self.id, None)

    def _update_cmap_from_color(self):
        cmap = get_translucent_cmap(*ColorConverter().to_rgb(self.state.color))
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

        if force or 'color' in changed:
            self._update_cmap_from_color()

        if force or 'vmin' in changed or 'vmax' in changed:
            self._update_limits()

        if force or 'alpha' in changed:
            self._update_alpha()

        if force or 'layer' in changed or 'attribute' in changed:
            self._update_data()

        if force or 'subset_mode' in changed:
            self._update_subset_mode()

        if force or 'visible' in changed:
            self._update_visibility()

    def update(self):
        self._update_volume(force=True)
        self.redraw()
