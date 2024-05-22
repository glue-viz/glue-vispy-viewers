
from glue_jupyter.view import IPyWidgetView
from ..volume_viewer import VispyVolumeViewerMixin
from .viewer_state_widget import Volume3DViewerStateWidget
from .layer_state_widget import Volume3DLayerStateWidget

__all__ = ['JupyterVispyVolumeViewer']


class JupyterVispyVolumeViewer(VispyVolumeViewerMixin, IPyWidgetView):

    _options_cls = Volume3DViewerStateWidget
    _layer_style_widget_cls = Volume3DLayerStateWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_widget_and_callbacks()
        self.create_layout()

    @property
    def figure_widget(self):
        return self._vispy_widget.canvas._backend
