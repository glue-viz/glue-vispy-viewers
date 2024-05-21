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

    cmap_attribute_items = traitlets.List().tag(sync=True)
    cmap_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    cmap_items = traitlets.List().tag(sync=True)

    # Points

    size_mode_items = traitlets.List().tag(sync=True)
    size_mode_selected = traitlets.Int(allow_none=True).tag(sync=True)

    size_attribute_items = traitlets.List().tag(sync=True)
    size_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Line

    linestyle_items = traitlets.List().tag(sync=True)
    linestyle_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Vectors

    vx_attribute_items = traitlets.List().tag(sync=True)
    vx_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    vy_attribute_items = traitlets.List().tag(sync=True)
    vy_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    vz_attribute_items = traitlets.List().tag(sync=True)
    vz_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    # Errors

    xerr_attribute_items = traitlets.List().tag(sync=True)
    xerr_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    yerr_attribute_items = traitlets.List().tag(sync=True)
    yerr_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    zerr_attribute_items = traitlets.List().tag(sync=True)
    zerr_attribute_selected = traitlets.Int(allow_none=True).tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        # Color

        link_glue_choices(self, layer_state, "color_mode")
        link_glue_choices(self, layer_state, "cmap_attribute")

        self.cmap_items = [
            {"text": cmap[0], "value": cmap[1].name} for cmap in colormaps.members
        ]

        # Size

        link_glue_choices(self, layer_state, "size_mode")
        link_glue_choices(self, layer_state, "size_attribute")

        # Vectors

        link_glue_choices(self, layer_state, "vx_attribute")
        link_glue_choices(self, layer_state, "vy_attribute")
        link_glue_choices(self, layer_state, "vz_attribute")

        # Error bars

        link_glue_choices(self, layer_state, "xerr_attribute")
        link_glue_choices(self, layer_state, "yerr_attribute")
        link_glue_choices(self, layer_state, "zerr_attribute")

    def vue_set_colormap(self, data):
        cmap = None
        for member in colormaps.members:
            if member[1].name == data:
                cmap = member[1]
                break
        self.layer_state.cmap = cmap
