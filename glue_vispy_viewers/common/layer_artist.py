from glue.core.layer_artist import LayerArtistBase

__all__ = ['VispyLayerArtist']


class VispyLayerArtist(LayerArtistBase):

    @property
    def zorder(self):
        return self.layer_state.zorder

    @zorder.setter
    def zorder(self, value):
        self.layer_state.zorder = value
        self.redraw()  # TODO: determine if this is needed

    @property
    def visible(self):
        return self.layer_state.visible

    @visible.setter
    def visible(self, value):
        self.layer_state.visible = value
        self._update_visibility()

    def __gluestate__(self, context):
        return dict(state=context.id(self.layer_state))
