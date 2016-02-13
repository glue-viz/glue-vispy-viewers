from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from vispy import scene
from vispy.geometry import create_cube
from glue.external.qt import QtGui, get_qapp

# TODO: Option to turn cube on/off

class VispyWidget(QtGui.QWidget):

    def __init__(self, parent=None):

        super(VispyWidget, self).__init__(parent=parent)

        # Prepare Vispy canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=False)

        # Set up a viewbox
        self.view = self.canvas.central_widget.add_view()
        self.view.parent = self.canvas.scene

        # Set whether we are emulating a 3D texture. This needs to be enabled
        # as a workaround on Windows otherwise VisPy crashes.
        self.emulate_texture = (sys.platform == 'win32' and
                                sys.version_info[0] < 3)

        self.scene_transform = scene.STTransform()
        self.limit_transforms = {}

        # Add a 3D cube to show us the unit cube
        vertices, filled_indices, outline_indices = create_cube()
        self.axis = scene.visuals.Mesh(vertices['position'], outline_indices,
                                       color=(1,1,1), mode='lines')
        self.axis.transform = self.scene_transform
        self.view.add(self.axis)

        # Create a turntable camera. For now, this is the only camerate type
        # we support, but if we support more in future, we should implement
        # that here
        self.view.camera = scene.cameras.TurntableCamera(parent=self.view.scene,
                                                         fov=60, distance=2)

        # Add the native canvas widget to this widget
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas.native)
        self.setLayout(layout)

        # We need to call render here otherwise we'll later encounter an OpenGL
        # program validation error.
        self.canvas.render()

    def add_data_visual(self, visual):
        self.limit_transforms[visual] = scene.STTransform()
        visual.transform = self.limit_transforms[visual]
        self.view.add(visual)

    def _update_stretch(self, *stretch):
        self.scene_transform.scale = stretch
        self._update_limits()

    def _update_attributes(self):
        pass

    def _update_limits(self):

        if len(self.limit_transforms) == 0:
            return

        if (self.options.x_min is None or self.options.x_max is None or
            self.options.y_min is None or self.options.y_max is None or
            self.options.z_min is None or self.options.z_max is None):
            raise Exception("We should never get here because if any data is "
                            "present, the limits should be set")

        scale = [2 / (self.options.x_max - self.options.x_min) * self.options.x_stretch,
                 2 / (self.options.y_max - self.options.y_min) * self.options.y_stretch,
                 2 / (self.options.z_max - self.options.z_min) * self.options.z_stretch]

        translate = [-0.5 * (self.options.x_min + self.options.x_max) * scale[0],
                     -0.5 * (self.options.y_min + self.options.y_max) * scale[1],
                     -0.5 * (self.options.z_min + self.options.z_max) * scale[2]]

        for visual in self.limit_transforms:
            self.limit_transforms[visual].scale = scale
            self.limit_transforms[visual].translate = translate

    def _reset_view(self):
        self.view.camera.reset()


if __name__ == "__main__":

    from viewer_options import VispyOptionsWidget

    app = get_qapp()
    w = VispyWidget()
    d = VispyOptionsWidget(vispy_widget=w)
    d.show()

    positions = np.random.random((1000, 3))
    scat_visual = scene.visuals.Markers()
    scat_visual.set_data(positions, symbol='disc', edge_color=None, face_color='red')
    w.add_data_visual(scat_visual)

    d.x_min = 0
    d.x_max = +1

    d.y_min = 0
    d.y_max = +1

    d.z_min = 0
    d.z_max = +1

    w.show()
    app.exec_()
    app.quit()
