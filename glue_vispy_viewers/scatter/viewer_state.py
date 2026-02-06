import warnings

from glue.viewers3d.scatter.viewer_state import ScatterViewerState3D

__all__ = ['Vispy3DScatterViewerState']

warnings.warn(
    "Importing Vispy3DScatterViewerState from glue_vispy_viewers.scatter.viewer_state is "
    "deprecated. Please import ScatterViewerState3D from glue.viewers3d.scatter.viewer_state "
    "instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
Vispy3DScatterViewerState = ScatterViewerState3D
