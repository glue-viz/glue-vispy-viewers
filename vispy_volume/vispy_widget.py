from __future__ import absolute_import, division, print_function
import numpy as np
from itertools import cycle

from glue.external.qt import QtGui, QtCore
from vispy import scene
from vispy.color import get_colormaps
from .colormaps import TransFire, TransGrays

__all__ = ['QtVispyWidget']


class QtVispyWidget(QtGui.QWidget):

    # Setup colormap iterators
    opaque_cmaps = cycle(get_colormaps())
    translucent_cmaps = cycle([TransFire(), TransGrays()])
    opaque_cmap = next(opaque_cmaps)
    translucent_cmap = next(translucent_cmaps)
    result = 1
    zoom_size = 0

    def __init__(self, parent=None):
        super(QtVispyWidget, self).__init__(parent=parent)

        # Prepare canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=True)
        self.canvas.measure_fps()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.canvas.central_widget.add_view()
        self.view.border_color = 'red'
        self.view.parent = self.canvas.scene

        # Set whether we are emulating a 3D texture
        self.emulate_texture = False

        self.data = None
        self.volume1 = None
        self.text = self.add_text_visual()
        self.text.pos = 80, self.canvas.size[1]/4

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        # Set up cameras
        self.cam1, self.cam2, self.cam3 = self.set_cam()
        self.view.camera = self.cam2  # Select turntable at firstate_texture=emulate_texture)

        # Connect events
        self.canvas.events.key_press.connect(self.on_key_press)
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)

    def set_data(self, data):
        self.data = data

    def set_subsets(self, subsets):
        self.subsets = subsets

    def add_volume_visual(self):

        # TODO: need to implement the visualiation of the subsets in this method

        if self.data is None:
            return

        vol1 = np.nan_to_num(np.array(self.data))

        # Create the volume visuals, only one is visible
        volume1 = scene.visuals.Volume(vol1, parent=self.view.scene, threshold=0.1,
                                       emulate_texture=self.emulate_texture)
        trans = (-vol1.shape[2]/2, -vol1.shape[1]/2, -vol1.shape[0]/2)
        volume1.transform = scene.STTransform(translate=trans)
        self.volume1 = volume1

    def add_text_visual(self):
        # Create the text visual to show zoom scale
        text = scene.visuals.Text('', parent=self.canvas.scene, color='white', bold=True, font_size=20)
        return text

    def set_cam(self):
        # Create two cameras (1 for firstperson, 3 for 3d person)
        fov = 60.
        cam1 = scene.cameras.FlyCamera(parent=self.view.scene, fov=fov, name='Fly')
        cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=fov,
                                            name='Turntable')
        cam3 = scene.cameras.ArcballCamera(parent=self.view.scene, fov=fov, name='Arcball')
        return cam1, cam2, cam3

    def on_mouse_wheel(self, event):
        self.zoom_size += event.delta[1]
        self.text.text = 'X %s' % round(self.zoom_size, 1)
        self.text.show = True

    # @canvas.events.key_press.connect
    def on_key_press(self, event):

        if self.view is None:
            return
        if event.text == '1':
            cam_toggle = {self.cam1: self.cam2, self.cam2: self.cam3, self.cam3: self.cam1}
            self.view.camera = cam_toggle.get(self.view.camera, self.cam2)
            self.canvas.render()
    #        print(view.camera.name + ' camera')
        elif event.text == '2':
            methods = ['mip', 'translucent', 'iso', 'additive']
            method = methods[(methods.index(self.volume1.method) + 1) % 4]
            print("Volume render method: %s" % method)
            cmap = self.opaque_cmap if method in ['mip', 'iso'] else self.translucent_cmap
            self.volume1.method = method
            self.volume1.cmap = cmap
        elif event.text == '3':
            self.volume1.visible = not self.volume1.visible

        # Color scheme cannot work now
        elif event.text == '4':
            if self.volume1.method in ['mip', 'iso']:
                cmap = self.opaque_cmap = next(self.opaque_cmaps)
            else:
                cmap = self.translucent_cmap = next(self.translucent_cmaps)
            self.volume1.cmap = cmap

        elif event.text == '0':
            self.cam1.set_range()
            self.cam3.set_range()
        elif event.text != '' and event.text in '[]':
            s = -0.025 if event.text == '[' else 0.025
            self.volume1.threshold += s
            th = self.volume1.threshold if self.volume1.visible else self.volume2.threshold
    #        print("Isosurface threshold: %0.3f" % th)
        # Add zoom out functionality for the third dimension
        elif event.text != '' and event.text in '=-':
            z = -1 if event.text == '-' else +1
            self.result += z
            if self.result > 0:
                self.volume1.transform = scene.STTransform(scale=(1, 1, self.result))
            else:
                self.result = 1
    #        print("Volume scale: %d" % result)
