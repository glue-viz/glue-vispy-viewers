import warnings

from glue.viewers.volume3d.viewer_state import VolumeViewerState3D

__all__ = ['Vispy3DVolumeViewerState']

warnings.warn(
    "Importing Vispy3DVolumeViewerState from glue_vispy_viewers.volume.viewer_state is deprecated. "
    "Please import VolumeViewerState3D from glue.viewers.volume3d.viewer_state instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
Vispy3DVolumeViewerState = VolumeViewerState3D
