from __future__ import absolute_import, division, print_function

import numpy as np
from glue.external.echo import CallbackProperty
from glue.core.state_objects import StateAttributeSingleValueHelper

from ..common.layer_state import VispyLayerState


__all__ = ['IsosurfaceLayerState']


class IsosurfaceLayerState(VispyLayerState):
    """
    A state object for volume layers
    """

    attribute = CallbackProperty()
    level = CallbackProperty()

    level_cache = CallbackProperty({})

    def __init__(self, **kwargs):

        super(IsosurfaceLayerState, self).__init__(**kwargs)

        def default_level(values):
            percentile = max((1 - 1e3 / values.size) * 100, 99)
            return np.percentile(values, percentile)

        self.level_helper = StateAttributeSingleValueHelper(self, 'attribute',
                                                            default_level,
                                                            value='level',
                                                            cache=self.level_cache)

    def update_priority(self, name):
        return 0 if name == 'level' else 1
