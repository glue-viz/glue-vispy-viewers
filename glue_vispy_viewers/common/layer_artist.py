from glue.viewers.common.layer_artist import LayerArtist

__all__ = ['VispyLayerArtist']


class VispyLayerArtist(LayerArtist):
    """
    Base class for Vispy layer artists.

    Provides common functionality for all Vispy-based layer artists including
    access to the vispy_widget and redraw behavior on zorder changes.
    """

    def __init__(self, vispy_viewer, layer_state=None, layer=None):

        # Store vispy_widget before calling super (needed for rendering)
        self.vispy_widget = vispy_viewer._vispy_widget

        # LayerArtist expects viewer_state, not viewer
        super(VispyLayerArtist, self).__init__(vispy_viewer.state,
                                               layer_state=layer_state,
                                               layer=layer)

    def redraw(self):
        """
        Redraw the Vispy canvas.

        Subclasses should override this if they need additional redraw logic.
        """
        if self.vispy_widget is not None:
            self.vispy_widget.canvas.update()

    def set_clip(self, limits):
        """
        Set clipping limits for the layer.

        Parameters
        ----------
        limits : tuple or None
            The clipping limits as (xmin, xmax, ymin, ymax, zmin, zmax) or None
        """
        pass  # Subclasses override as needed

    @property
    def visual(self):
        """
        The Vispy visual object for this layer.

        Subclasses must override this property.
        """
        raise NotImplementedError("Subclasses must implement the visual property")
