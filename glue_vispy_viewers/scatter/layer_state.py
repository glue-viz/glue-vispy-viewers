import warnings

from glue.viewers3d.scatter.layer_state import ScatterLayerState

__all__ = ['ScatterLayerState']

warnings.warn(
    "Importing ScatterLayerState from glue_vispy_viewers.scatter.layer_state is deprecated. "
    "Please import ScatterLayerState from glue.viewers3d.scatter.layer_state instead.",
    DeprecationWarning,
    stacklevel=2
)
