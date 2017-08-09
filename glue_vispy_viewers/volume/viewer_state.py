from glue_vispy_viewers.common.viewer_state import Vispy3DViewerState

__all__ = ['VispyVolume3DViewerState']


class Vispy3DVolumeViewerState(Vispy3DViewerState):

    def __init__(self, **kwargs):

        super(Vispy3DVolumeViewerState, self).__init__()

        self.add_callback('layers', self._update_attributes)

        self.update_from_dict(kwargs)

    def _update_attributes(self, *args):

        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) == 3:
                data = layer_state.layer
                break
        else:
            data = None

        if data is None:

            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        else:

            z_cid, y_cid, x_cid = data.pixel_component_ids

            type(self).x_att.set_choices(self, [x_cid])
            type(self).y_att.set_choices(self, [y_cid])
            type(self).z_att.set_choices(self, [z_cid])
