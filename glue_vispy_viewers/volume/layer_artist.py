from __future__ import absolute_import, division, print_function

import sys

from glue.core.data import Subset
from glue.core.layer_artist import LayerArtistBase

from .volume_visual import MultiVolume
from .volume_visual_legacy import MultiVolume as MultiVolumeLegacy


class VolumeLayerArtist(LayerArtistBase):
    """
    A layer artist to render volumes.

    This is more complex than for other visual types, because for volumes, we
    need to manage all the volumes via a single MultiVolume visual class for
    each data viewer.
    """

    def __init__(self, layer, vispy_viewer):

        super(VolumeLayerArtist, self).__init__(layer)

        self.layer = layer
        self.vispy_viewer = vispy_viewer

        # We need to use MultiVolume instance to store volumes, but we should
        # only have one per canvas. Therefore, we store the MultiVolume
        # instance in the vispy viewer instance.
        if not hasattr(vispy_viewer, '_multivol'):

            # Set whether we are emulating a 3D texture. This needs to be
            # enabled as a workaround on Windows otherwise VisPy crashes.
            emulate_texture = (sys.platform == 'win32' and
                               sys.version_info[0] < 3)

            try:
                multivol = MultiVolume(threshold=0.1, emulate_texture=emulate_texture)
            except:
                multivol = MultiVolumeLegacy(threshold=0.1, emulate_texture=emulate_texture)

            self.vispy_viewer.add_data_visual(multivol)
            vispy_viewer._multivol = multivol

        self._multivol = vispy_viewer._multivol
        self._multivol.allocate(self.layer.label)

    @property
    def bbox(self):
        return (0, self.layer.shape[2],
                0, self.layer.shape[1],
                0, self.layer.shape[0])

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._update_visibility()

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self.vispy_viewer.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """
        self._multivol.deallocate(self.layer.label)

    def update(self):
        """
        Update the visualization to reflect the underlying data
        """
        self.redraw()
        self._changed = False

    def set_cmap(self, cmap):
        self._multivol.set_cmap(self.layer.label, cmap)
        self.redraw()

    def set_clim(self, clim):
        self._multivol.set_clim(self.layer.label, clim)
        self.redraw()

    def set_alpha(self, alpha):
        self._multivol.set_weight(self.layer.label, alpha)
        self.redraw()

    def set_attribute(self, attribute):
        self._attribute = attribute
        self._update_data()

    def _update_data(self):
        if isinstance(self.layer, Subset):
            data = self.layer.to_mask().astype(float)
        else:
            data = self.layer[self._attribute]
        self._multivol.set_data(self.layer.label, data)
        self.redraw()

    def _update_visibility(self):
        if self.visible:
            self._multivol.enable(self.layer.label)
        else:
            self._multivol.disable(self.layer.label)
        self.redraw()
