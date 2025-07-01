import ipyvuetify as v
import traitlets

from glue.core.coordinate_helpers import world_axis
from glue.viewers.image.state import AggregateSlice
from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.vuetify_helpers import link_glue_choices

__all__ = ["Volume3DViewerStateWidget"]


class Volume3DViewerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "viewer_state_widget.vue")

    glue_state = GlueState().tag(sync=True)

    reference_data_items = traitlets.List().tag(sync=True)
    reference_data_selected = traitlets.Int(allow_none=True).tag(sync=True)

    x_att_items = traitlets.List().tag(sync=True)
    x_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    y_att_items = traitlets.List().tag(sync=True)
    y_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    z_att_items = traitlets.List().tag(sync=True)
    z_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    resolution_items = traitlets.List().tag(sync=True)
    resolution_selected = traitlets.Int(allow_none=True).tag(sync=True)

    sliders = traitlets.List().tag(sync=True)

    def __init__(self, viewer_state):

        super().__init__()

        self.viewer_state = viewer_state
        self.glue_state = viewer_state

        link_glue_choices(self, viewer_state, "reference_data")
        link_glue_choices(self, viewer_state, "x_att")
        link_glue_choices(self, viewer_state, "y_att")
        link_glue_choices(self, viewer_state, "z_att")
        link_glue_choices(self, viewer_state, "resolution")

        for prop in ['x_att', 'y_att', 'z_att', 'slices', 'reference_data']:
            viewer_state.add_callback(prop, self._sync_sliders_from_state)

        self._sync_sliders_from_state()

    def _sync_sliders_from_state(self, *not_used):

        if self.viewer_state.reference_data is None or self.viewer_state.slices is None:
            return

        if self.viewer_state.x_att is None or \
           self.viewer_state.y_att is None or \
           self.viewer_state.z_att is None:
               return

        data = self.viewer_state.reference_data

        def used_on_axis(index):
            return index in [self.viewer_state.x_att.axis,
                             self.viewer_state.y_att.axis,
                             self.viewer_state.z_att.axis]

        new_slices = []
        for i in range(data.ndim):
            slice = self.viewer_state.slices[i]
            if not used_on_axis(i) and isinstance(slice, AggregateSlice):
                new_slices.append(slice.center)
            else:
                new_slices.append(slice)
        self.viewer_state.slices = tuple(new_slices)

        self.sliders = [{
            'index': i,
            'label': (data.world_component_ids[i].label if data.coords
                      else data.pixel_component_ids[i].label),
            'max': data.shape[i] - 1,
            'unit': (data.get_component(data.world_component_ids[i]).units if data.coords
                     else ''),
            'world_value': ("%0.4E" % world_axis(data.coords,
                                                 data,
                                                 pixel_axis=data.ndim - 1 - i,
                                                 world_axis=data.ndim - 1 - i
                                                 )[self.glue_state.slices[i]] if data.coords
                            else '')
        } for i in range(data.ndim) if not used_on_axis(i)]
