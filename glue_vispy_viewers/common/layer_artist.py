from glue.core.layer_artist import LayerArtistBase

__all__ = ['VispyLayerArtist']


class VispyLayerArtist(LayerArtistBase):

    @property
    def zorder(self):
        return self.state.zorder

    @zorder.setter
    def zorder(self, value):
        self.state.zorder = value
        self.redraw()  # TODO: determine if this is needed

    @property
    def visible(self):
        return self.state.visible

    @visible.setter
    def visible(self, value):
        self.state.visible = value

    def __gluestate__(self, context):
        return dict(state=context.id(self.state))
