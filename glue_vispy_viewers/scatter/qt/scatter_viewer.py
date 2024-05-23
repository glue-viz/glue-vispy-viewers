from ...common.qt.data_viewer import BaseVispyViewer
from .layer_style_widget import ScatterLayerStyleWidget

from ..scatter_viewer import VispyScatterViewerMixin


class VispyScatterViewer(VispyScatterViewerMixin, BaseVispyViewer):

    _layer_style_widget_cls = ScatterLayerStyleWidget
