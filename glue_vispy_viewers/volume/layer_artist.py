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

    def __init__(self, canvas=None, view=None):

        super(VolumeLayerArtist, self).__init__()

        # Keep a reference to the canvas
        self.canvas = canvas

        # We need to use MultiVolume instance to store volumes, but we should
        # only have one per canvas. Therefore, we store the MultiVolume
        # instance in the canvas.
        if not hasattr(canvas, '_multivol'):

            # Set whether we are emulating a 3D texture. This needs to be
            # enabled as a workaround on Windows otherwise VisPy crashes.
            emulate_texture = (sys.platform == 'win32' and
                               sys.version_info[0] < 3)

            try:
                canvas._multivol = MultiVolume(parent=view.scene, threshold=0.1,
                                               emulate_texture=emulate_texture)
            except:
                canvas._multivol = MultiVolumeLegacy(parent=self.view.scene, threshold=0.1,
                                                     emulate_texture=emulate_texture)

        self._multivol = canvas._multivol
        
    @property
    def visible(self):
        return self._visible
        
    @visible.setter
    def visible(self, value):
        print("SETTING VISIBILITY", value)
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
