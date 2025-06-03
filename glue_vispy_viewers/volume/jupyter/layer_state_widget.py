import ipyvuetify as v
import traitlets

from glue.config import colormaps
from glue.core.subset import Subset

from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.vuetify_helpers import link_glue_choices

__all__ = ["Volume3DLayerStateWidget"]


class Volume3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_state_widget.vue")

    glue_state = GlueState().tag(sync=True)

    attribute_items = traitlets.List().tag(sync=True)
    attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Color

    color_mode_items = traitlets.List().tag(sync=True)
    color_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_items = traitlets.List().tag(sync=True)

    subset = traitlets.Bool().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        self.subset = isinstance(layer_state.layer, Subset)

        link_glue_choices(self, layer_state, "attribute")
        link_glue_choices(self, layer_state, "color_mode")

        self.cmap_items = [
            {"text": cmap[0], "value": cmap[1].name} for cmap in colormaps.members
        ]

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break
        self.layer_state.cmap = cmap
