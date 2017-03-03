from __future__ import absolute_import, division, print_function

from glue.config import colormaps
from glue.external.echo import CallbackProperty, keep_in_sync
from glue.core.state_objects import StateAttributeLimitsHelper
from ..common.layer_state import VispyLayerState

__all__ = ['ScatterLayerState']


class ScatterLayerState(VispyLayerState):
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
    cmap_attribute = CallbackProperty()
    cmap_vmin = CallbackProperty()
    cmap_vmax = CallbackProperty()
    cmap = CallbackProperty()

    size_limits_cache = CallbackProperty({})
    cmap_limits_cache = CallbackProperty({})

    def __init__(self, **kwargs):

        self._sync_markersize = None

        super(ScatterLayerState, self).__init__(**kwargs)

        if self.layer is not None:

            if self.cmap_attribute is None:
                self.cmap_attribute = self.layer.visible_components[0]

            if self.size_attribute is None:
                self.size_attribute = self.layer.visible_components[0]

            self.color = self.layer.style.color
            self.size = self.layer.style.markersize
            self.alpha = self.layer.style.alpha

        self.size_att_helper = StateAttributeLimitsHelper(self, attribute='size_attribute',
                                                          lower='size_vmin', upper='size_vmax',
                                                          cache=self.size_limits_cache)

        self.cmap_att_helper = StateAttributeLimitsHelper(self, attribute='cmap_attribute',
                                                          lower='cmap_vmin', upper='cmap_vmax',
                                                          cache=self.cmap_limits_cache)

        if self.cmap is None:
            self.cmap = colormaps.members[0][1]

    def update_priority(self, name):
        return 0 if name.endswith(('vmin', 'vmax')) else 1

    def _layer_changed(self):

        super(ScatterLayerState, self)._layer_changed()

        if self._sync_markersize is not None:
            self._sync_markersize.stop_syncing()

        if self.layer is not None:
            self.size = self.layer.style.markersize
            self._sync_color = keep_in_sync(self, 'size', self.layer.style, 'markersize')

    def flip_size(self):
        self.size_att_helper.flip_limits()

    def flip_cmap(self):
        self.cmap_att_helper.flip_limits()
