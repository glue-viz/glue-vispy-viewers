__author__ = 'penny'

import numpy as np

from ..extern.vispy import app, scene, io
from ..extern.vispy.visuals.transforms import STTransform
from ..utils import as_matrix_transform


# TODO: ticks and labels will be implemented here

class CornerXYZAxis(scene.visuals.XYZAxis):
    # Axes are x=red, y=green, z=blue.
    def __init__(self, vispy_widget=None, *args, **kwargs):

        super(CornerXYZAxis, self).__init__(*args, **kwargs)
        
        try:
            self.unfreeze()
        except AttributeError:  # VisPy <= 0.4
            pass

        # Initiate a transform
        s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))

        affine = s.as_matrix()

        # TODO: here we needs the transform from camera system to visual system
        tr = as_matrix_transform(self.get_transform(map_from='visual', map_to='scene'))  # I want from camera to canvas
        result = np.dot(affine, tr)
        print('affine, tr, result', affine, tr, result)
        self.transform = result

        self._vispy_widget = vispy_widget

        # Connect callback functions to VisPy Canvas
        self._vispy_widget.canvas.events.mouse_move.connect(self.on_mouse_move)
        
        try:
            self.freeze()
        except AttributeError:  # VisPy <= 0.4
            pass

    @property
    def camera(self):
        # TurntableCamera
        return self._vispy_widget.view.camera

    # Implement axis connection with self.camera
    def on_mouse_move(self, event):
        if event.button == 1 and event.is_dragging:
            print('scene_transform', self._vispy_widget.scene_transform)
            self.transform.reset()

            self.transform.rotate(self.camera.elevation, (1, 0, 0))
            self.transform.rotate(self.camera.azimuth, (0, 1, 0))

            self.transform.scale((50, 50, 0.001))
            self.transform.translate((50., 50.))
            self.update()

    # TODO: add axis text

