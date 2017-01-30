from __future__ import absolute_import, division, print_function

from glue.core import Subset
from glue.external.echo import CallbackProperty
from glue.core.state_objects import State, StateAttributeLimitsHelper

__all__ = ['VolumeLayerState']


class VolumeLayerState(State):
    """
    A state object for volume layers
    """

    attribute = CallbackProperty()
    vmin = CallbackProperty()
    vmax = CallbackProperty()
    color = CallbackProperty()
    alpha = CallbackProperty()
    subset_mode = CallbackProperty('data')

    def __init__(self, layer, **kwargs):

        super(VolumeLayerState, self).__init__(**kwargs)

        self.layer = layer

        self.att_helper = StateAttributeLimitsHelper(self, attribute='attribute',
                                                     vlo='vmin', vhi='vmax')

        self.color = self.layer.style.color
        self.alpha = self.layer.style.alpha

        if isinstance(self.layer, Subset):
            self.vmin = 0
            self.att_helper.vlo_frozen = True
