import weakref
from glue_jupyter.common.toolbar_vuetify import BasicJupyterToolbar
from ..toolbar import VispyViewerToolbarMixin

__all__ = ['VispyJupyterToolbar']


class VispyJupyterToolbar(VispyViewerToolbarMixin, BasicJupyterToolbar):

    def __init__(self, viewer=None, **kwargs):
        BasicJupyterToolbar.__init__(self, viewer, **kwargs)
        self._viewer = weakref.ref(viewer)

    @property
    def viewer(self):
        return self._viewer()

    def activate_tool(self, mode):
        self._enable_tool_interactions(mode)

    def deactivate_tool(self, mode):
        self._disable_tool_interactions(mode)
