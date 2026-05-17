import ipyvuetify as v
from ipywidgets import DOMWidget, widget_serialization
from traitlets import Instance

from echo.vue import autoconnect_callbacks_to_vue
from glue_jupyter.common.slice_helpers import MultiSliceWidgetHelper


__all__ = ["Volume3DViewerStateWidget"]


class Volume3DViewerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "viewer_state_widget.vue")

    widget_slices = Instance(DOMWidget, allow_none=True).tag(sync=True, **widget_serialization)

    def __init__(self, viewer_state):
        super().__init__()

        self.state = viewer_state

        self.slice_helper = MultiSliceWidgetHelper(viewer_state)
        self.widget_slices = self.slice_helper.layout

        autoconnect_callbacks_to_vue(viewer_state, self, extras={"resolution": "selection"})
