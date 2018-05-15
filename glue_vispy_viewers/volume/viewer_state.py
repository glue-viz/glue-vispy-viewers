from glue.external.echo import CallbackProperty, SelectionCallbackProperty
from glue_vispy_viewers.common.viewer_state import Vispy3DViewerState

__all__ = ['Vispy3DVolumeViewerState']


class Vispy3DVolumeViewerState(Vispy3DViewerState):

    downsample = CallbackProperty(True)
    resolution = SelectionCallbackProperty(4)

    def __init__(self, **kwargs):

        super(Vispy3DVolumeViewerState, self).__init__()

        self.add_callback('layers', self._update_attributes)

        Vispy3DVolumeViewerState.resolution.set_choices(self, [2**i for i in range(4, 12)])

        self.update_from_dict(kwargs)

    def _first_3d_data(self):
        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) == 3:
                return layer_state.layer

    def _update_attributes(self, *args):

        data = self._first_3d_data()

        if data is None:

            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        else:

            z_cid, y_cid, x_cid = data.pixel_component_ids

            type(self).x_att.set_choices(self, [x_cid])
            type(self).y_att.set_choices(self, [y_cid])
            type(self).z_att.set_choices(self, [z_cid])

    @property
    def clip_limits_relative(self):

        data = self._first_3d_data()

        if data is None:
            return [0., 1., 0., 1., 0., 1.]
        else:
            nz, ny, nx = data.shape
            return (self.x_min / nx,
                    self.x_max / nx,
                    self.y_min / ny,
                    self.y_max / ny,
                    self.z_min / nz,
                    self.z_max / nz)
