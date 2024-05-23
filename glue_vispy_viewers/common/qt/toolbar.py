import weakref

from glue_qt.viewers.common.toolbar import BasicToolbar
from ..toolbar import VispyViewerToolbarMixin

__all__ = ['VispyQtToolbar']


class VispyQtToolbar(VispyViewerToolbarMixin, BasicToolbar):

    def __init__(self, viewer=None, **kwargs):
        BasicToolbar.__init__(self, viewer, **kwargs)
        self._viewer = weakref.ref(viewer)

    @property
    def viewer(self):
        return self._viewer()
