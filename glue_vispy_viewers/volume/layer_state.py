from __future__ import absolute_import, division, print_function

from glue.core import Subset
from glue.external.echo import CallbackProperty
from glue.core.state_objects import StateAttributeLimitsHelper
from ..common.layer_state import VispyLayerState

__all__ = ['VolumeLayerState']


class VolumeLayerState(VispyLayerState):
    """
    A state object for volume layers
    """

    attribute = CallbackProperty()
    vmin = CallbackProperty()
    vmax = CallbackProperty()
    subset_mode = CallbackProperty('data')
    limits_cache = CallbackProperty({})

    def __init__(self, **kwargs):

        super(VolumeLayerState, self).__init__(**kwargs)

        if self.layer is not None:

            if self.attribute is None:
                self.attribute = self.layer.visible_components[0]

            self.color = self.layer.style.color
            self.alpha = self.layer.style.alpha

        self.att_helper = StateAttributeLimitsHelper(self, attribute='attribute',
                                                     lower='vmin', upper='vmax',
                                                     cache=self.limits_cache)

        if isinstance(self.layer, Subset):
            self.vmin = 0
            self.att_helper.lower_frozen = True

    def update_priority(self, name):
        return 0 if name.endswith(('vmin', 'vmax')) else 1
