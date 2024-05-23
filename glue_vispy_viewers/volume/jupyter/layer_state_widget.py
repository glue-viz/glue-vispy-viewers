import ipyvuetify as v
import traitlets

from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.vuetify_helpers import link_glue_choices

__all__ = ["Volume3DLayerStateWidget"]


class Volume3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_state_widget.vue")

    glue_state = GlueState().tag(sync=True)

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        link_glue_choices(self, layer_state, "attribute")
