import ipyvuetify as v
import traitlets

from echo.vue import autoconnect_callbacks_to_vue
from glue.core.subset import Subset
from glue_jupyter.vuetify_helpers import cmap_extras


__all__ = ["Volume3DLayerStateWidget"]


class Volume3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "layer_state_widget.vue")

    subset = traitlets.Bool().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

        self.layer_state = layer_state
        self.glue_state = layer_state

        self.subset = isinstance(layer_state.layer, Subset)

        extras = {"cmap": cmap_extras(self)}
        autoconnect_callbacks_to_vue(layer_state, self, extras=extras, skip={"subset"})
