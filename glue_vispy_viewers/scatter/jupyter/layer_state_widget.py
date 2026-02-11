import ipyvuetify as v
import traitlets

from glue.config import colormaps

from glue_jupyter.state_traitlets_helpers import GlueState
from glue_jupyter.vuetify_helpers import link_glue_choices

__all__ = ["Scatter3DLayerStateWidget"]


class Scatter3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_state_widget.vue")

    glue_state = GlueState().tag(sync=True)

    # Color

    color_mode_items = traitlets.List().tag(sync=True)
    color_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_att_items = traitlets.List().tag(sync=True)
    cmap_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_items = traitlets.List().tag(sync=True)

    # Points

    size_mode_items = traitlets.List().tag(sync=True)
    size_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    size_att_items = traitlets.List().tag(sync=True)
    size_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Line

    linestyle_items = traitlets.List().tag(sync=True)
    linestyle_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Vectors

    vx_att_items = traitlets.List().tag(sync=True)
    vx_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    vy_att_items = traitlets.List().tag(sync=True)
    vy_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    vz_att_items = traitlets.List().tag(sync=True)
    vz_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Errors

    xerr_att_items = traitlets.List().tag(sync=True)
    xerr_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    yerr_att_items = traitlets.List().tag(sync=True)
    yerr_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    zerr_att_items = traitlets.List().tag(sync=True)
    zerr_att_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        # Color

        link_glue_choices(self, layer_state, "color_mode")
        link_glue_choices(self, layer_state, "cmap_att")

        self.cmap_items = [
            {"text": cmap[0], "value": cmap[1].name} for cmap in colormaps.members
        ]

        # Size

        link_glue_choices(self, layer_state, "size_mode")
        link_glue_choices(self, layer_state, "size_att")

        # Vectors

        link_glue_choices(self, layer_state, "vx_att")
        link_glue_choices(self, layer_state, "vy_att")
        link_glue_choices(self, layer_state, "vz_att")

        # Error bars

        link_glue_choices(self, layer_state, "xerr_att")
        link_glue_choices(self, layer_state, "yerr_att")
        link_glue_choices(self, layer_state, "zerr_att")

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break
        self.layer_state.cmap = cmap
