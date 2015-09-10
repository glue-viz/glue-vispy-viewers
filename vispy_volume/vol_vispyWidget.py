from __future__ import absolute_import, division, print_function
import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app
from vispy.color import get_colormap

__all__ = ['QtVispyWidget']


class QtVispyWidget(QtGui.QWidget):

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
        self.zoom_size = 0
        self.zoom_text = self.add_text_visual()
        self.zoom_timer = app.Timer(0.2, connect=self.on_timer, start=False)

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.widget_axis_scale = [1, 1, 1]

        # Set up cameras
        self.cam1, self.cam2 = self.set_cam()
        # self.cam_dist = 100 # Set a default value as 100
        self.view.camera = self.cam2  # Select turntable at firstate_texture=emulate_texture)

        # Set up default colormap
        self.color_map = get_colormap('hsl')

        # Connect events
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.resize.connect(self.on_resize)

    def set_data(self, data):
        self.data = data

    def set_subsets(self, subsets):
        self.subsets = subsets

    def get_data(self):
        if self.data is None:
            return None
        else:
            vol1 = np.nan_to_num(np.array(self.data))
            return vol1

    def add_volume_visual(self):

        # TODO: need to implement the visualiation of the subsets in this method

        # if self.data is None:
        #     return

        # vol1 = np.nan_to_num(np.array(self.data))

        vol1 = self.get_data()
        # Create the volume visual and give default settings
        volume1 = scene.visuals.Volume(vol1, parent=self.view.scene, threshold=0.1, method='mip',
                                       emulate_texture=self.emulate_texture)
        volume1.cmap = self.color_map

        trans = (-vol1.shape[2]/2, -vol1.shape[1]/2, -vol1.shape[0]/2)
        _axis_scale = (vol1.shape[2], vol1.shape[1], vol1.shape[0])
        volume1.transform = scene.STTransform(translate=trans)

        self.axis.transform = scene.STTransform(translate=trans, scale=_axis_scale)
        # self.cam2.distance = vol1.shape[1]

        self.volume1 = volume1
        self.widget_axis_scale = self.axis.transform.scale


    def add_text_visual(self):
        # Create the text visual to show zoom scale
        text = scene.visuals.Text('', parent=self.canvas.scene, color='white', bold=True, font_size=16)
        text.pos = [40, self.canvas.size[1]-40]
        return text

    def on_timer(self, event):
        self.zoom_text.color = [1,1,1,float((7-event.iteration) % 8)/8]
        self.canvas.update()

    def on_resize(self, event):
        self.zoom_text.pos = [40, self.canvas.size[1]-40]

    def set_cam(self):
        # Create two cameras (1 for firstperson, 3 for 3d person)
        fov = 60.
        '''
        The fly camera provides a way to explore 3D data using an interaction style that resembles a flight simulator.
        Moving:

        * arrow keys, or WASD to move forward, backward, left and right
        * F and C keys move up and down
        * Space bar to brake

        Viewing:

        * Use the mouse while holding down LMB to control the pitch and yaw.
        * Alternatively, the pitch and yaw can be changed using the keys
            IKJL
        * The camera auto-rotates to make the bottom point down, manual
            rolling can be performed using Q and E.
        '''
        cam1 = scene.cameras.FlyCamera(parent=self.view.scene, fov=fov, name='Fly')

        # 3D camera class that orbits around a center point while maintaining a view on a center point.
        cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=fov,
                                            name='Turntable', center=(0, 0, 0))
        return cam1, cam2

    def on_mouse_wheel(self, event):
        self.zoom_size += event.delta[1]
        self.zoom_text.text = 'X %s' % round(self.zoom_size, 1)
        self.zoom_timer.start(interval=0.2, iterations=8)


