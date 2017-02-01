from __future__ import absolute_import, division, print_function

import numpy as np

from glue.external.echo import CallbackProperty, delay_callback
from glue.core.state_objects import State, StateAttributeLimitsHelper

__all__ = ['Vispy3DViewerState']


class Vispy3DViewerState(State):
    """
    A common state object for all vispy 3D viewers
    """

    x_att = CallbackProperty()
    x_min = CallbackProperty(0)
    x_max = CallbackProperty(1)
    x_stretch = CallbackProperty(1.)

    y_att = CallbackProperty()
    y_min = CallbackProperty(0)
    y_max = CallbackProperty(1)
    y_stretch = CallbackProperty(1.)

    z_att = CallbackProperty()
    z_min = CallbackProperty(0)
    z_max = CallbackProperty(1)
    z_stretch = CallbackProperty(1.)

    visible_axes = CallbackProperty(True)
    perspective_view = CallbackProperty(False)
    clip_data = CallbackProperty(False)
    native_aspect = CallbackProperty(False)

    def __init__(self, **kwargs):

        super(Vispy3DViewerState, self).__init__(**kwargs)

        self.limits_cache = {}

        self.x_att_helper = StateAttributeLimitsHelper(self, attribute='x_att',
                                                       lower='x_min', upper='x_max',
                                                       limits_cache=self.limits_cache)

        self.y_att_helper = StateAttributeLimitsHelper(self, attribute='y_att',
                                                       lower='y_min', upper='y_max',
                                                       limits_cache=self.limits_cache)

        self.z_att_helper = StateAttributeLimitsHelper(self, attribute='z_att',
                                                       lower='z_min', upper='z_max',
                                                       limits_cache=self.limits_cache)

    @property
    def aspect(self):
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
        self.x_att_helper.flip_limits()

    def flip_y(self):
        self.y_att_helper.flip_limits()

    def flip_z(self):
        self.z_att_helper.flip_limits()

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
