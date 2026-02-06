# Re-export VolumeViewerState3D as Vispy3DVolumeViewerState for backwards compatibility
from glue.viewers3d.volume.viewer_state import VolumeViewerState3D as Vispy3DVolumeViewerState

__all__ = ['Vispy3DVolumeViewerState']
