from glue.core.data import BaseData
from echo import CallbackProperty, SelectionCallbackProperty, delay_callback
from glue_vispy_viewers.common.viewer_state import Vispy3DViewerState
from glue.core.data_combo_helper import ManualDataComboHelper

from glue.viewers.image.state import AggregateSlice

__all__ = ['Vispy3DVolumeViewerState']


class Vispy3DVolumeViewerState(Vispy3DViewerState):

    downsample = CallbackProperty(True)
    resolution = SelectionCallbackProperty(4)
    slices = CallbackProperty(docstring='The current slice along all dimensions')
    reference_data = SelectionCallbackProperty(docstring='The dataset that is used to define the '
                                                         'available pixel/world components, and '
                                                         'which defines the coordinate frame in '
                                                         'which the images are shown')

    def __init__(self, **kwargs):

        super(Vispy3DVolumeViewerState, self).__init__()

        self.ref_data_helper = ManualDataComboHelper(self, 'reference_data')
        self.slices = ()

        self.add_callback('layers', self._layers_changed, echo_old=True)
        self.add_callback('x_att', self._on_xatt_changed, echo_old=True)
        self.add_callback('y_att', self._on_yatt_changed, echo_old=True)
        self.add_callback('z_att', self._on_zatt_changed, echo_old=True)

        self._layers_changed(None, self.layers)

        Vispy3DVolumeViewerState.resolution.set_choices(self, [2**i for i in range(4, 12)])

        self.update_from_dict(kwargs)

    def _first_3d_data(self):
        for layer_state in self.layers:
            if getattr(layer_state.layer, 'ndim', None) >= 3:
                return layer_state.layer

    def _layers_changed(self, old_layers, new_layers):
        if self.reference_data is not None and old_layers == new_layers:
            return
        self._update_combo_ref_data()
        self._set_reference_data()
        self._update_attributes()

    def _update_combo_ref_data(self, *args):
        self.ref_data_helper.set_multiple_data(self.layers_data)

    def _set_reference_data(self, *args):
        if self.reference_data is None:
            self.slices = ()
            for layer in self.layers:
                if isinstance(layer.layer, BaseData):
                    self.reference_data = layer.layer
                    return
        else:
            self.slices = (0,) * self.reference_data.ndim

    def _update_attributes(self, *args):

        data = self._first_3d_data()

        if data is None:

            type(self).x_att.set_choices(self, [])
            type(self).y_att.set_choices(self, [])
            type(self).z_att.set_choices(self, [])

        else:
            pixel_ids = data.pixel_component_ids
            with delay_callback(self, "x_att", "y_att", "z_att"):
                type(self).x_att.set_choices(self, pixel_ids)
                type(self).y_att.set_choices(self, pixel_ids)
                type(self).z_att.set_choices(self, pixel_ids)

    def _set_up_attributes(self, *args):
        data = self._first_3d_data()
        if data is not None:
            pixel_ids = data.pixel_component_ids
            self.x_att = pixel_ids[2]
            self.y_att = pixel_ids[1]
            self.z_att = pixel_ids[0]

    @property
    def numpy_slice_permutation(self):
        if self.reference_data is None:
            return None, None

        slices = []
        coord_att_axes = [self.x_att.axis, self.y_att.axis, self.z_att.axis]
        for i in range(self.reference_data.ndim):
            if i in coord_att_axes:
                slices.append(slice(None))
            else:
                if isinstance(self.slices[i], AggregateSlice):
                    slices.append(self.slices[i].slice)
                else:
                    slices.append(self.slices[i])

        perm = [0] * 3
        for i, t in enumerate(coord_att_axes):
            perm[t] = i
        return slices, perm 

    @property
    def clip_limits_relative(self):

        data = self._first_3d_data()

        if data is None:
            return [0., 1., 0., 1., 0., 1.]
        else:
            nx = data.shape[self.x_att.axis]
            ny = data.shape[self.y_att.axis]
            nz = data.shape[self.z_att.axis]
            return (self.x_min / nx,
                    self.x_max / nx,
                    self.y_min / ny,
                    self.y_max / ny,
                    self.z_min / nz,
                    self.z_max / nz)

    def _on_xatt_changed(self, prev_att, new_att):
        if self.y_att == new_att:
            self.y_att = prev_att
        elif self.z_att == new_att:
            self.z_att = prev_att

    def _on_yatt_changed(self, prev_att, new_att):
        if self.x_att == new_att:
            self.x_att = prev_att
        elif self.z_att == new_att:
            self.z_att = prev_att

    def _on_zatt_changed(self, prev_att, new_att):
        if self.x_att == new_att:
            self.x_att = prev_att
        elif self.y_att == new_att:
            self.y_att = prev_att
