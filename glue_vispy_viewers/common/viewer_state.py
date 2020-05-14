import numpy as np

from glue.external.echo import (CallbackProperty, SelectionCallbackProperty,
                                delay_callback, ListCallbackProperty)
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.viewers.common.state import ViewerState

__all__ = ['Vispy3DViewerState']


class Vispy3DViewerState(ViewerState):
    """
    A common state object for all vispy 3D viewers
    """

    x_att = SelectionCallbackProperty()
    x_min = CallbackProperty(0)
    x_max = CallbackProperty(1)
    x_stretch = CallbackProperty(1.)

    y_att = SelectionCallbackProperty(default_index=1)
    y_min = CallbackProperty(0)
    y_max = CallbackProperty(1)
    y_stretch = CallbackProperty(1.)

    z_att = SelectionCallbackProperty(default_index=2)
    z_min = CallbackProperty(0)
    z_max = CallbackProperty(1)
    z_stretch = CallbackProperty(1.)

    x_axislabel = CallbackProperty('', docstring='Label for the x-axis')
    y_axislabel = CallbackProperty('', docstring='Label for the y-axis')
    z_axislabel = CallbackProperty('', docstring='Label for the z-axis')

    x_axislabel_size = CallbackProperty(10, docstring='Size of the x-axis label')
    y_axislabel_size = CallbackProperty(10, docstring='Size of the y-axis label')
    z_axislabel_size = CallbackProperty(10, docstring='Size of the z-axis label')

    x_axislabel_bold = CallbackProperty(False, docstring='Weight of the x-axis label')
    y_axislabel_bold = CallbackProperty(False, docstring='Weight of the y-axis label')
    z_axislabel_bold = CallbackProperty(False, docstring='Weight of the z-axis label')

    x_ticklabel_size = CallbackProperty(8, docstring='Size of the x-axis tick labels')
    y_ticklabel_size = CallbackProperty(8, docstring='Size of the y-axis tick labels')
    z_ticklabel_size = CallbackProperty(8, docstring='Size of the z-axis tick labels')

    visible_axes = CallbackProperty(True)
    perspective_view = CallbackProperty(False)
    clip_data = CallbackProperty(True)
    native_aspect = CallbackProperty(False)

    layers = ListCallbackProperty()

    limits_cache = CallbackProperty()

    def _update_priority(self, name):
        if name == 'layers':
            return 2
        elif name.endswith(('_min', '_max')):
            return 0
        else:
            return 1

    def __init__(self, **kwargs):

        super(Vispy3DViewerState, self).__init__(**kwargs)

        if self.limits_cache is None:
            self.limits_cache = {}

        self.x_lim_helper = StateAttributeLimitsHelper(self, attribute='x_att',
                                                       lower='x_min', upper='x_max',
                                                       cache=self.limits_cache)

        self.y_lim_helper = StateAttributeLimitsHelper(self, attribute='y_att',
                                                       lower='y_min', upper='y_max',
                                                       cache=self.limits_cache)

        self.z_lim_helper = StateAttributeLimitsHelper(self, attribute='z_att',
                                                       lower='z_min', upper='z_max',
                                                       cache=self.limits_cache)

        # TODO: if limits_cache is re-assigned to a different object, we need to
        # update the attribute helpers. However if in future we make limits_cache
        # into a smart dictionary that can call callbacks when elements are
        # changed then we shouldn't always call this. It'd also be nice to
        # avoid this altogether and make it more clean.
        self.add_callback('limits_cache', self._update_limits_cache)

        self.add_callback('x_att', self._on_x_att_change)
        self.add_callback('y_att', self._on_y_att_change)
        self.add_callback('z_att', self._on_z_att_change)

    def _on_x_att_change(self, *args):
        self.x_axislabel = '' if self.x_att is None else self.x_att.label

    def _on_y_att_change(self, *args):
        self.y_axislabel = '' if self.y_att is None else self.y_att.label

    def _on_z_att_change(self, *args):
        self.z_axislabel = '' if self.z_att is None else self.z_att.label

    def reset_limits(self):
        self.x_lim_helper.log = False
        self.x_lim_helper.percentile = 100.
        self.x_lim_helper.update_values(force=True)
        self.y_lim_helper.log = False
        self.y_lim_helper.percentile = 100.
        self.y_lim_helper.update_values(force=True)
        self.z_lim_helper.log = False
        self.z_lim_helper.percentile = 100.
        self.z_lim_helper.update_values(force=True)

    def _update_limits_cache(self, *args):
        self.x_lim_helper._cache = self.limits_cache
        self.x_lim_helper._update_attribute()
        self.y_lim_helper._cache = self.limits_cache
        self.y_lim_helper._update_attribute()
        self.z_lim_helper._cache = self.limits_cache
        self.z_lim_helper._update_attribute()

    @property
    def aspect(self):
        # TODO: this could be cached based on the limits, but is not urgent
        aspect = np.array([1, 1, 1], dtype=float)
        if self.native_aspect:
            aspect[0] = 1.
            aspect[1] = (self.y_max - self.y_min) / (self.x_max - self.x_min)
            aspect[2] = (self.z_max - self.z_min) / (self.x_max - self.x_min)
            aspect /= aspect.max()
        return aspect

    def reset(self):
        pass

    def flip_x(self):
        self.x_lim_helper.flip_limits()

    def flip_y(self):
        self.y_lim_helper.flip_limits()

    def flip_z(self):
        self.z_lim_helper.flip_limits()

    @property
    def clip_limits(self):
        return (self.x_min, self.x_max,
                self.y_min, self.y_max,
                self.z_min, self.z_max)

    def set_limits(self, x_min, x_max, y_min, y_max, z_min, z_max):
        with delay_callback(self, 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'):
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max
            self.z_min = z_min
            self.z_max = z_max
