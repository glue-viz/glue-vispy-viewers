from __future__ import absolute_import, division, print_function

import sys

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
                vispy_viewer._multivol = MultiVolume(threshold=0.1,
                                                     emulate_texture=emulate_texture)
            except:
                vispy_viewer._multivol = MultiVolumeLegacy(threshold=0.1,
                                                           emulate_texture=emulate_texture)

        self._multivol = vispy_viewer._multivol

        self.vispy_viewer.add_data_visual(self._multivol)

        self._set_data()

    def _set_data(self):
        # For now, hard code which attribute is picked
        data = self.layer['PRIMARY']
        self._multivol.set_volume('data', data, (data.min(), data.max()), 'grays')

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

    def redraw(self):
        """
        Redraw the Vispy canvas
        """
        self.canvas.update()

    def clear(self):
        """
        Remove the layer artist from the visualization
        """

    def update(self):
        """
        """
