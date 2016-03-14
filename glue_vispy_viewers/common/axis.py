__author__ = 'penny'

import numpy as np

from vispy import app, scene, io
from vispy.visuals.transforms import STTransform


# TODO: ticks and labels will be implemented here

class CornerXYZAxis(scene.visuals.XYZAxis):
    def __init__(self, vispy_widget=None, *args, **kwargs):

        super(CornerXYZAxis, self).__init__(*args, **kwargs)
        self.unfreeze()

        # Initiate a transform
        s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))
        affine = s.as_matrix()
        self.transform = affine
        self._vispy_widget = vispy_widget

        # Connect callback functions to VisPy Canvas
        self._vispy_widget.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.freeze()

    @property
    def camera(self):
        return self._vispy_widget.view.camera

    # Implement axis connection with self.camera
    def on_mouse_move(self, event):
        if event.button == 1 and event.is_dragging:
            self.transform.reset()

            self.transform.rotate(self.camera.roll, (0, 0, 1))
            self.transform.rotate(self.camera.elevation, (1, 0, 0))
            self.transform.rotate(self.camera.azimuth, (0, 1, 0))

            self.transform.scale((50, 50, 0.001))
            self.transform.translate((50., 50.))
            self.update()

    # TODO: add axis text

