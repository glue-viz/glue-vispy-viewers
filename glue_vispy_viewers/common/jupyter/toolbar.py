from glue_jupyter.common.toolbar_vuetify import BasicJupyterToolbar
from ..toolbar import VispyViewerToolbarMixin

__all__ = ['VispyJupyterToolbar']


class VispyJupyterToolbar(VispyViewerToolbarMixin, BasicJupyterToolbar):

    def __init__(self, viewer=None, **kwargs):
        BasicJupyterToolbar.__init__(self, viewer, **kwargs)
        self.viewer = viewer
