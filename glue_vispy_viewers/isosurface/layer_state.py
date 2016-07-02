from __future__ import absolute_import, division, print_function

from glue.config import colormaps
from glue.external.echo import CallbackProperty
from glue.core.state_objects import StateAttributeLimitsHelper

from ..common.layer_state import VispyLayerState


__all__ = ['IsosurfaceLayerState']


class IsosurfaceLayerState(VispyLayerState):
    """
    A state object for volume layers
    """

    attribute = CallbackProperty()

    level_low = CallbackProperty()
    level_high = CallbackProperty()
    cmap = CallbackProperty()
    step = CallbackProperty()
    step_value = CallbackProperty()

    level_cache = CallbackProperty({})

    def __init__(self, **kwargs):

        super(IsosurfaceLayerState, self).__init__(**kwargs)

        self.level_helper = StateAttributeLimitsHelper(self, attribute='attribute',
                                                       lower='level_low', upper='level_high')

        if self.cmap is None:
            self.cmap = colormaps.members[0][1]

    def update_priority(self, name):
        return 0 if name == 'level' else 1
