from glue.core.data_combo_helper import ComponentIDComboHelper
from glue_vispy_viewers.common.viewer_state import Vispy3DViewerState

__all__ = ['Vispy3DScatterViewerState']


class Vispy3DScatterViewerState(Vispy3DViewerState):

    def __init__(self, **kwargs):

        super(Vispy3DScatterViewerState, self).__init__()

        self.x_att_helper = ComponentIDComboHelper(self, 'x_att', categorical=False)
        self.y_att_helper = ComponentIDComboHelper(self, 'y_att', categorical=False)
        self.z_att_helper = ComponentIDComboHelper(self, 'z_att', categorical=False)

        self.add_callback('layers', self._on_layers_change)

        self.update_from_dict(kwargs)

    def _on_layers_change(self, *args):
        layers_data = [layer_state.layer for layer_state in self.layers]
        self.x_att_helper.set_multiple_data(layers_data)
        self.y_att_helper.set_multiple_data(layers_data)
        self.z_att_helper.set_multiple_data(layers_data)
