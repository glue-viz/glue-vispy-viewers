from glue_jupyter.view import IPyWidgetView
from ..scatter_viewer import VispyScatterViewerMixin


class JupyterVispyScatterViewer(VispyScatterViewerMixin, IPyWidgetView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_widget_and_callbacks()

    @property
    def figure_widget(self):
        return self._vispy_widget.canvas
