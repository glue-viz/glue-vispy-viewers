import warnings

from glue.viewers3d.common.viewer_state import ViewerState3D

__all__ = ['Vispy3DViewerState']

warnings.warn(
    "Importing Vispy3DViewerState from glue_vispy_viewers.common.viewer_state is deprecated. "
    "Please import ViewerState3D from glue.viewers3d.common.viewer_state instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
Vispy3DViewerState = ViewerState3D
