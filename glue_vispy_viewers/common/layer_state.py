import warnings

from glue.viewers.common3d.layer_state import LayerState3D

__all__ = ['VispyLayerState']

warnings.warn(
    "Importing VispyLayerState from glue_vispy_viewers.common.layer_state is deprecated. "
    "Please import LayerState3D from glue.viewers.common3d.layer_state instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
VispyLayerState = LayerState3D
