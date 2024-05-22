
from glue_jupyter.view import IPyWidgetView
from ..scatter_viewer import VispyScatterViewerMixin
from .viewer_state_widget import Scatter3DViewerStateWidget
from .layer_state_widget import Scatter3DLayerStateWidget

__all__ = ['JupyterVispyScatterViewer']


class JupyterVispyScatterViewer(VispyScatterViewerMixin, IPyWidgetView):

    _options_cls = Scatter3DViewerStateWidget
    _layer_style_widget_cls = Scatter3DLayerStateWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_widget_and_callbacks()
        self.create_layout()

    @property
    def figure_widget(self):
        return self._vispy_widget.canvas._backend