from __future__ import absolute_import, division, print_function

import sys

from vispy import scene
from glue.external.qt import QtGui, get_qapp


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

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        # Create a turntable camera. For now, this is the only camerate type
        # we support, but if we support more in future, we should implement
        # that here
        self.view.camera = scene.cameras.TurntableCamera(parent=self.view.scene,
                                                         fov=90)

        # Add the native canvas widget to this widget
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas.native)
        self.setLayout(layout)

    def _update_stretch(self):
        pass

    def _update_attributes(self):
        pass

    def _update_limits(self):
        pass

    def _reset_view(self):
        self.view.camera.reset()


if __name__ == "__main__":

    from viewer_options import VispyOptionsWidget

    app = get_qapp()
    w = VispyWidget()
    d = VispyOptionsWidget(vispy_widget=w)
    d.show()
    w.show()
    app.exec_()
    app.quit()
