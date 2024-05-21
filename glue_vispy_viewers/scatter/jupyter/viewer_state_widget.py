import ipyvuetify as v
import traitlets

from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.vuetify_helpers import link_glue_choices

__all__ = ["Scatter3DViewerStateWidget"]


class Scatter3DViewerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "viewer_state_widget.vue")

    glue_state = GlueState().tag(sync=True)

    x_att_items = traitlets.List().tag(sync=True)
    x_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    y_att_items = traitlets.List().tag(sync=True)
    y_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    z_att_items = traitlets.List().tag(sync=True)
    z_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, viewer_state):

        super().__init__()

        self.viewer_state = viewer_state
        self.glue_state = viewer_state

        link_glue_choices(self, viewer_state, "x_att")
        link_glue_choices(self, viewer_state, "y_att")
        link_glue_choices(self, viewer_state, "z_att")

        # TODO: expose line width on viewer state?
