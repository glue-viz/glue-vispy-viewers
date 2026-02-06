import warnings

from glue.viewers3d.volume.layer_state import VolumeLayerState

__all__ = ['VolumeLayerState']

warnings.warn(
    "Importing VolumeLayerState from glue_vispy_viewers.volume.layer_state is deprecated. "
    "Please import VolumeLayerState from glue.viewers3d.volume.layer_state instead.",
    DeprecationWarning,
    stacklevel=2
)
