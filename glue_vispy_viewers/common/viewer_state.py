# Re-export ViewerState3D as Vispy3DViewerState for backwards compatibility
from glue.viewers3d.common.viewer_state import ViewerState3D as Vispy3DViewerState

__all__ = ['Vispy3DViewerState']
