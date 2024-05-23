import os
from glue_jupyter.view import IPyWidgetView
from ..scatter_viewer import VispyScatterViewerMixin
from .viewer_state_widget import Scatter3DViewerStateWidget
from .layer_state_widget import Scatter3DLayerStateWidget
from ...common.jupyter.toolbar import VispyJupyterToolbar

__all__ = ['JupyterVispyScatterViewer']


class JupyterVispyScatterViewer(VispyScatterViewerMixin, IPyWidgetView):

    _options_cls = Scatter3DViewerStateWidget
    _layer_style_widget_cls = Scatter3DLayerStateWidget
    _toolbar_cls = VispyJupyterToolbar

    def __init__(self, *args, **kwargs):
        # Vispy and jupyter_rfb don't work correctly on Linux unless DISPLAY is set
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'
        super().__init__(*args, **kwargs)
        self.setup_widget_and_callbacks()
        self.create_layout()

    @property
    def figure_widget(self):
        return self._vispy_widget.canvas._backend
