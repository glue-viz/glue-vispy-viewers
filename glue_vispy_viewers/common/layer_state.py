# Re-export LayerState3D as VispyLayerState for backwards compatibility
from glue.viewers3d.common.layer_state import LayerState3D as VispyLayerState

__all__ = ['VispyLayerState']
