from __future__ import absolute_import, division, print_function

from glue.config import colormaps
from glue.external.echo import CallbackProperty
from glue.core.state_objects import State, StateAttributeLimitsHelper

__all__ = ['ScatterLayerState']


class ScatterLayerState(State):
    """
    A state object for volume layers
    """

    size_mode = CallbackProperty('Fixed')
    size = CallbackProperty()
    size_attribute = CallbackProperty()
    size_vmin = CallbackProperty()
    size_vmax = CallbackProperty()
    size_scaling = CallbackProperty(1)

    color_mode = CallbackProperty('Fixed')
    color = CallbackProperty()
    cmap_attribute = CallbackProperty()
    cmap_vmin = CallbackProperty()
    cmap_vmax = CallbackProperty()
    cmap = CallbackProperty()
    alpha = CallbackProperty()

    layer = CallbackProperty()

    def __init__(self, **kwargs):

        super(ScatterLayerState, self).__init__(**kwargs)

        self.size_att_helper = StateAttributeLimitsHelper(self, attribute='size_attribute',
                                                          lower='size_vmin', upper='size_vmax')

        self.cmap_att_helper = StateAttributeLimitsHelper(self, attribute='cmap_attribute',
                                                          lower='cmap_vmin', upper='cmap_vmax')

        self.color = self.layer.style.color
        self.size = self.layer.style.markersize
        self.alpha = self.layer.style.alpha

        if self.cmap is None:
            self.cmap = colormaps.members[0][1]
