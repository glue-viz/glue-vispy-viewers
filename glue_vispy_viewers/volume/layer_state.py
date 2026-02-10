import warnings

from glue.viewers.volume3d.layer_state import VolumeLayerState3D as VolumeLayerState

__all__ = ['VolumeLayerState']

warnings.warn(
    "Importing VolumeLayerState from glue_vispy_viewers.volume.layer_state is deprecated. "
    "Please import VolumeLayerState from glue.viewers.volume3d.layer_state instead.",
    DeprecationWarning,
    stacklevel=2
)
