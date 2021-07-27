from glue.config import colormaps
from echo import CallbackProperty, SelectionCallbackProperty, delay_callback
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.core.data_combo_helper import ComponentIDComboHelper

from ..common.layer_state import VispyLayerState


__all__ = ['IsosurfaceLayerState']


class IsosurfaceLayerState(VispyLayerState):
    """
    A state object for volume layers
    """

    attribute = SelectionCallbackProperty()

    level_low = CallbackProperty()
    level_high = CallbackProperty()
    cmap = CallbackProperty()
    step = CallbackProperty(4)

    level_cache = CallbackProperty({})

    def __init__(self, layer=None, **kwargs):

        super(IsosurfaceLayerState, self).__init__(layer=layer)

        self.att_helper = ComponentIDComboHelper(self, 'attribute')

        self.lim_helper = StateAttributeLimitsHelper(self, attribute='attribute',
                                                     lower='level_low', upper='level_high')

        self.add_callback('layer', self._on_layer_change)
        if layer is not None:
            self._on_layer_change()

        self.cmap = colormaps.members[0][1]

        self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):

        with delay_callback(self, 'level_low', 'level_high'):

            if self.layer is None:
                self.att_helper.set_multiple_data([])
            else:
                self.att_helper.set_multiple_data([self.layer])

    def update_priority(self, name):
        return 0 if name == 'level' else 1
