# Re-export ScatterViewerState3D as Vispy3DScatterViewerState for backwards compatibility
from glue.viewers3d.scatter.viewer_state import ScatterViewerState3D as Vispy3DScatterViewerState

__all__ = ['Vispy3DScatterViewerState']
