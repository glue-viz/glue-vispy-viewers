from echo import CallbackProperty, SelectionCallbackProperty
from glue.config import colormaps
from glue.viewers.volume3d.layer_state import VolumeLayerState3D

__all__ = ['VolumeLayerState']


class VolumeLayerState(VolumeLayerState3D):
    """Volume layer state with vispy-only extensions.

    Subclasses ``glue.viewers.volume3d.layer_state.VolumeLayerState``
    and adds attributes that only make sense for the vispy-based volume
    renderer, so they aren't visible from non-vispy frontends (notably
    ipyvolume) which would otherwise ignore them. If/when those become
    cross-frontend concepts they can be lifted into glue-core.
    """

    cut_plane_color_mode = SelectionCallbackProperty(
        0, choices=['Fixed', 'Linear']
    )
    cut_plane_color = CallbackProperty()
    cut_plane_cmap = CallbackProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # SelectionCallbackProperty stores choices per-instance via a WeakKeyDictionary
        # populated lazily on first ``get_choices`` lookup. Force the dictionary to be
        # populated now so the choices are bound to the instance (rather than only to
        # the class) and survive a round-trip through ``__setgluestate__``.
        VolumeLayerState.cut_plane_color_mode.set_choices(self, ['Fixed', 'Linear'])

        self.cut_plane_cmap = self.cmap

        self.update_from_dict(kwargs)

    @property
    def cut_plane_cmap_name(self):
        return colormaps.name_from_cmap(self.cut_plane_cmap)
