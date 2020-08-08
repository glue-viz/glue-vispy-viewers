import uuid

import numpy as np

from glue.core.exceptions import IncompatibleAttribute
from glue.utils import categorical_ndarray

from .multi_scatter import MultiColorScatter
from .layer_state import ScatterLayerState
from ..common.layer_artist import VispyLayerArtist

from vispy.scene.visuals import Line, Arrow

from matplotlib.colors import ColorConverter

COLOR_PROPERTIES = set(['color_mode', 'cmap_attribute', 'cmap_vmin', 'cmap_vmax', 'cmap', 'color'])
SIZE_PROPERTIES = set(['size_mode', 'size_attribute', 'size_vmin', 'size_vmax',
                       'size_scaling', 'size'])
ALPHA_PROPERTIES = set(['alpha'])
DATA_PROPERTIES = set(['layer', 'x_att', 'y_att', 'z_att'])
ERROR_PROPERTIES = set(['xerr_visible', 'yerr_visible', 'zerr_visible', 'xerr_attribute', 'yerr_attribute', 'zerr_attribute'])
VECTOR_PROPERTIES = set(['vector_visible', 'vx_attribute', 'vy_attribute', 'vz_attribute', 'vector_scaling', 'vector_origin', 'vector_arrowhead'])
VISIBLE_PROPERTIES = set(['visible'])


class ScatterLayerArtist(VispyLayerArtist):
    """
    A layer artist to render 3d scatter plots.
    """

    def __init__(self, vispy_viewer, layer=None, layer_state=None):

        super(ScatterLayerArtist, self).__init__(layer)

        self._clip_limits = None

        # Set data caches
        self._marker_data = None
        self._color_data = None
        self._size_data = None

        self.layer = layer or layer_state.layer
        self.vispy_widget = vispy_viewer._vispy_widget

        # TODO: need to remove layers when layer artist is removed
        self._viewer_state = vispy_viewer.state
        self.state = layer_state or ScatterLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

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

        self._error_vector_widget = Arrow(connect="segments", parent=self._multiscat)

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._update_scatter)
        self.state.add_global_callback(self._update_scatter)

        self.reset_cache()

    def reset_cache(self):
        self._last_viewer_state = {}
        self._last_layer_state = {}

    @property
    def visual(self):
        return self._multiscat

    def get_zorder(self):
        return self.zorder

    def get_layer_color(self):
        if self.state.color_mode == 'Fixed':
            return self.state.color
        else:
            return self.state.cmap

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        if self._multiscat is not None:
            self._multiscat._update()
        self.vispy_widget.canvas.update()

    def clear(self):
        """
        Clear the visualization for this layer
        """
        self._multiscat.set_data_values(self.id, [], [], [])
        self._error_vector_widget.set_data(pos=[], arrows=[])

    def remove(self):
        """
        Remove the layer artist from the visualization
        """

        if self._multiscat is None:
            return

        self._multiscat.deallocate(self.id)
        self._multiscat = None

        self._viewer_state.remove_global_callback(self._update_scatter)
        self.state.remove_global_callback(self._update_scatter)

    def _update_sizes(self):
        if self.state.size_mode is None:
            pass
        elif self.state.size_mode == 'Fixed':
            self._multiscat.set_size(self.id, self.state.size * self.state.size_scaling)
        else:
            data = self.layer[self.state.size_attribute].ravel()
            if isinstance(data, categorical_ndarray):
                data = data.codes
            if self.state.size_vmax == self.state.size_vmin:
                size = np.ones(data.shape) * 10
            else:
                size = (20 * (data - self.state.size_vmin) /
                        (self.state.size_vmax - self.state.size_vmin))
            size_data = size * self.state.size_scaling
            size_data[np.isnan(data)] = 0.
            self._multiscat.set_size(self.id, size_data)

    def _compute_cmap(self):
        if self.state.color_mode is None or self.state.color_mode == 'Fixed':
            self._color_data = None
        data = self.layer[self.state.cmap_attribute].ravel()
        if isinstance(data, categorical_ndarray):
            data = data.codes
        if self.state.cmap_vmax == self.state.cmap_vmin:
            cmap_data = np.ones(data.shape) * 0.5
        else:
            cmap_data = ((data - self.state.cmap_vmin) /
                         (self.state.cmap_vmax - self.state.cmap_vmin))
        cmap_data = self.state.cmap(cmap_data)
        cmap_data[:, 3][np.isnan(data)] = 0.
        self._color_data = cmap_data

    def _update_colors(self):
        if self.state.color_mode is None:
            pass
        elif self.state.color_mode == 'Fixed':
            self._multiscat.set_color(self.id, self.state.color)
        else:
            if self._color_data is None:
                self._compute_cmap()
            self._multiscat.set_color(self.id, self._color_data)

    def _update_errors_vectors_colors(self):
        if self.state.color_mode is None:
            pass
        elif self.state.color_mode == 'Fixed':
            color = ColorConverter.to_rgba(self.state.color, alpha=self.state.alpha)
            self._error_vector_widget.set_data(color=color)
            self._error_vector_widget.arrow_color=color
        else:
            if self._color_data is None:
                self._compute_cmap()
            res = self._get_cmap_array(self._color_data, self._error_vector_widget.pos.shape[0])
            self._error_vector_widget.set_data(color=res)
            self._error_vector_widget.arrow_color=self._color_data*self.state.alpha

    def _update_alpha(self):
        self._multiscat.set_alpha(self.id, self.state.alpha)

    def _update_data(self, event=None):

        try:
            x = self.layer[self._viewer_state.x_att].ravel()
            y = self.layer[self._viewer_state.y_att].ravel()
            z = self.layer[self._viewer_state.z_att].ravel()
        except AttributeError:
            return
        except (IncompatibleAttribute, IndexError):
            # The following includes a call to self.clear()
            self.disable_invalid_attributes(self._viewer_state.x_att,
                                            self._viewer_state.y_att,
                                            self._viewer_state.z_att)
            return
        else:
            self._enabled = True

        self._marker_data = np.array([x, y, z]).transpose()

        # We need to make sure we update the sizes and colors in case
        # these were set as arrays, since the size of the data might have
        # changed (in the case of subsets)

        self._multiscat.set_data_values(self.id, x, y, z)

        # Mask points outside the clip limits
        if self._clip_limits is None:
            self._multiscat.set_mask(self.id, None)
        else:
            xmin, xmax, ymin, ymax, zmin, zmax = self._clip_limits
            keep = (x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax) & (z >= zmin) & (z <= zmax)
            self._multiscat.set_mask(self.id, keep)

        self.redraw()

    def _update_visibility(self):
        self._multiscat.set_visible(self.id, self.visible)
        self.redraw()

    def _update_errors_vectors(self):
        offsets = {'tail': (0, 1), 'middle': (-0.5, 0.5), 'tip': (-1, 0)}
        orig_points = self._multiscat.layers[self.id]['data']
        num_points = orig_points.shape[0]
        num_bars = (self.state.xerr_visible + self.state.yerr_visible + self.state.zerr_visible \
                    + self.state.vector_visible) * num_points
        if not self.state.visible or num_bars < 0:
            self._error_vector_widget.visible = False
            return
        self._error_vector_widget.visible = True
        line_points = np.zeros((2*num_bars,3))
        arrow_points = np.zeros((self.state.vector_visible*num_points, 6))
        offset = 0
        if self.state.xerr_visible:
            err = self.layer[self.state.xerr_attribute].ravel()
            line_points[offset  :offset+num_points*2:2, :] = orig_points
            line_points[offset+1:offset+num_points*2:2, :] = orig_points
            line_points[offset  :offset+num_points*2:2, 0] -= err
            line_points[offset+1:offset+num_points*2:2, 0] += err
            offset += 2*num_points
        if self.state.yerr_visible:
            err = self.layer[self.state.yerr_attribute].ravel()
            line_points[offset:offset + num_points * 2:2, :] = orig_points
            line_points[offset + 1:offset + num_points * 2:2, :] = orig_points
            line_points[offset:offset + num_points * 2:2, 1] -= err
            line_points[offset + 1:offset + num_points * 2:2, 1] += err
            offset += 2 * num_points
        if self.state.zerr_visible:
            err = self.layer[self.state.zerr_attribute].ravel()
            line_points[offset  :offset+num_points*2:2, :] = orig_points
            line_points[offset+1:offset+num_points*2:2, :] = orig_points
            line_points[offset  :offset+num_points*2:2, 2] -= err
            line_points[offset+1:offset+num_points*2:2, 2] += err
            offset += 2*num_points
        if self.state.vector_visible:
            vec_offset = offsets[self.state.vector_origin]
            scale = self.state.vector_scaling
            vx = self.layer[self.state.vx_attribute].ravel()
            arrow_points[:, 0] = orig_points[:, 0] + vec_offset[0] * vx * scale
            arrow_points[:, 3] = orig_points[:, 0] + vec_offset[1] * vx * scale
            vy = self.layer[self.state.vy_attribute].ravel()
            arrow_points[:, 1] = orig_points[:, 1] + vec_offset[0] * vy * scale
            arrow_points[:, 4] = orig_points[:, 1] + vec_offset[1] * vy * scale
            vz = self.layer[self.state.vz_attribute].ravel()
            arrow_points[:, 2] = orig_points[:, 2] + vec_offset[0] * vz * scale
            arrow_points[:, 5] = orig_points[:, 2] + vec_offset[1] * vz * scale
            line_points[offset:,:] = arrow_points.reshape(-1,3)
        self._error_vector_widget.set_data(pos=line_points, arrows=arrow_points if self.state.vector_arrowhead else [])

    def _get_cmap_array(self, color_data, dest_size):
        res = np.zeros((dest_size, color_data.shape[1]))
        offset = 0
        while offset < dest_size:
            res[offset  :offset+color_data.shape[0]*2:2] = color_data
            res[offset+1:offset+color_data.shape[0]*2:2] = color_data
            offset += 2*color_data.shape[0]
        res[:,3] *= self.state.alpha
        return res


    @property
    def default_limits(self):
        if self._marker_data is None:
            raise ValueError("Data not yet set")
        dmin = np.nanmin(self._marker_data, axis=0)
        dmax = np.nanmax(self._marker_data, axis=0)
        # TODO: the following can be optimized
        return tuple(np.array([dmin, dmax]).transpose().ravel())

    def set_clip(self, limits):
        self._clip_limits = limits
        self._update_data()

    def _update_scatter(self, force=False, **kwargs):

        if (self._viewer_state.x_att is None or
            self._viewer_state.y_att is None or
            self._viewer_state.z_att is None or
                self.state.layer is None):
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
            force = True

        if force or len(changed & SIZE_PROPERTIES) > 0:
            self._update_sizes()

        if force or len(changed & COLOR_PROPERTIES) > 0:
            self._color_data = None
            self._update_colors()
            self._update_errors_vectors_colors()

        if force or len(changed & ALPHA_PROPERTIES) > 0:
            self._update_alpha()
            self._update_errors_vectors_colors()

        if force or len(changed & VISIBLE_PROPERTIES) > 0:
            self._update_visibility()
            self._update_errors_vectors()

        if force or len(changed & ERROR_PROPERTIES) > 0:
            self._update_errors_vectors()
            self._update_errors_vectors_colors()

        if force or len(changed & VECTOR_PROPERTIES) > 0:
            self._update_errors_vectors()
            self._update_errors_vectors_colors()

    def update(self):
        with self._multiscat.delay_update():
            self._update_scatter(force=True)
        self.redraw()
