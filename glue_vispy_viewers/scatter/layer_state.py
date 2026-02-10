import warnings

from glue.viewers.scatter3d.layer_state import ScatterLayerState3D as ScatterLayerState

__all__ = ['ScatterLayerState']

warnings.warn(
    "Importing ScatterLayerState from glue_vispy_viewers.scatter.layer_state is deprecated. "
    "Please import ScatterLayerState from glue.viewers.scatter3d.layer_state instead.",
    DeprecationWarning,
    stacklevel=2
)
