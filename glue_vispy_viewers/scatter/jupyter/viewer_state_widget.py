import ipyvuetify as v

from echo.vue import autoconnect_callbacks_to_vue


__all__ = ["Scatter3DViewerStateWidget"]


class Scatter3DViewerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, "viewer_state_widget.vue")

    def __init__(self, viewer_state):
        super().__init__()

        self.viewer_state = viewer_state
        autoconnect_callbacks_to_vue(viewer_state, self)
