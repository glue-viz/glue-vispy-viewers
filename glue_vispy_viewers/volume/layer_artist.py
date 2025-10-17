import uuid
import weakref

import numpy as np

from matplotlib.colors import ColorConverter

from glue.core.data import Subset, Data
from glue.core.link_manager import equivalent_pixel_cids, pixel_cid_to_pixel_cid_matrix
from glue.core.exceptions import IncompatibleAttribute
from glue.core.fixed_resolution_buffer import ARRAY_CACHE, PIXEL_CACHE
from .colors import get_mpl_cmap, get_translucent_cmap
from .layer_state import VolumeLayerState
from ..common.layer_artist import VispyLayerArtist


COLOR_PROPERTIES = set(['cmap', 'color', 'color_mode', 'stretch', 'stretch_parameters'])


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

    def _pixel_cid_order(self):
        mat = pixel_cid_to_pixel_cid_matrix(self.viewer_state.reference_data,
                                            self.layer_artist.layer)
        order = []
        for i in range(mat.shape[1]):
            idx = np.argmax(mat[:, i])
            order.append(idx if mat[idx, i] else None)
        return order


    @property
    def shape(self):

        order = self._pixel_cid_order()

        try:
            x_axis = order.index(self.viewer_state.x_att.axis)
            y_axis = order.index(self.viewer_state.y_att.axis)
            z_axis = order.index(self.viewer_state.z_att.axis)
        except (AttributeError, ValueError):
            self.layer_artist.disable('Layer data is not fully linked to reference data')
            return 0, 0, 0

        if isinstance(self.layer_artist.layer, Subset):
            full_shape = self.layer_artist.layer.data.shape
        else:
            full_shape = self.layer_artist.layer.shape

        return full_shape[z_axis], full_shape[y_axis], full_shape[x_axis]

    def compute_fixed_resolution_buffer(self, bounds=None):

        shape = [bound[2] for bound in bounds]

        if self.layer_artist is None or self.viewer_state is None:
            return np.broadcast_to(0, shape)

        order = self._pixel_cid_order()
        reference_axes = [self.viewer_state.x_att.axis,
                          self.viewer_state.y_att.axis,
                          self.viewer_state.z_att.axis]
        if order is not None and not set(reference_axes) <= set(order):
            self.layer_artist.disable('Layer data is not fully linked to x/y/z attributes')
            return np.broadcast_to(0, shape)

        # For this method, we make use of Data.compute_fixed_resolution_buffer,
        # which requires us to specify bounds in the form (min, max, nsteps).
        # We also allow view to be passed here (which is a normal Numpy view)
        # and, if given, translate it to bounds. If neither are specified,
        # we behave as if view was [slice(None), slice(None), slice(None)].

        def slice_to_bound(slc, size):
            min, max, step = slc.indices(size)
            n = (max - min - 1) // step
            max = min + step * n
            return (min, max, n + 1)

        full_view, permutation = self.viewer_state.numpy_slice_permutation

        full_view[reference_axes[0]] = bounds[2]
        full_view[reference_axes[1]] = bounds[1]
        full_view[reference_axes[2]] = bounds[0]

        layer = self.layer_artist.layer
        for i in range(self.viewer_state.reference_data.ndim):
            if isinstance(full_view[i], slice):
                full_view[i] = slice_to_bound(full_view[i],
                                              self.viewer_state.reference_data.shape[i])

        if isinstance(layer, Subset):
            try:
                subset_state = layer.subset_state
                result = layer.data.compute_fixed_resolution_buffer(
                    full_view,
                    target_data=self.viewer_state.reference_data,
                    subset_state=subset_state,
                    cache_id=self.layer_artist.id)
            except IncompatibleAttribute:
                self.layer_artist.disable_incompatible_subset()
                return np.broadcast_to(0, shape)
            else:
                self.layer_artist.enable()
        else:
            try:
                result = layer.compute_fixed_resolution_buffer(
                    full_view,
                    target_data=self.viewer_state.reference_data,
                    target_cid=self.layer_artist.state.attribute,
                    cache_id=self.layer_artist.id)
            except IncompatibleAttribute:
                self.layer_artist.disable('Layer data is not fully linked to reference data')
                return np.broadcast_to(0, shape)
            else:
                self.layer_artist.enable()

        if permutation:
            try:
                result = result.transpose(permutation)
            except ValueError:
                return np.broadcast_to(0, shape)

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
