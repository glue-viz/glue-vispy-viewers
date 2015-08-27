from __future__ import absolute_import, division, print_function
import numpy as np
from glue.external.qt import QtGui, QtCore
from vispy import scene, app
from vispy.color import get_colormaps, get_colormap

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
        self.cam1, self.cam2, self.cam3 = self.set_cam()
        # self.cam_dist = 100 # Set a default value as 100
        self.view.camera = self.cam2  # Select turntable at firstate_texture=emulate_texture)

        # Set up default colormap
        self.color_map = get_colormap('autumn')

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

        # Create the volume visual and give default settings
        volume1 = scene.visuals.Volume(vol1, parent=self.view.scene, threshold=0.1, method='mip',
                                       emulate_texture=self.emulate_texture)
        volume1.cmap = self.color_map

        trans = (-vol1.shape[2]/2, -vol1.shape[1]/2, -vol1.shape[0]/2)
        _axis_scale = (vol1.shape[2], vol1.shape[1], vol1.shape[0])
        volume1.transform = scene.STTransform(translate=trans)

        self.axis.transform = scene.STTransform(translate=trans, scale=_axis_scale)
        self.cam2.distance = self.cam3.distance = vol1.shape[1]

        self.volume1 = volume1
        self.widget_axis_scale = self.axis.transform.scale


    def add_text_visual(self):
        # Create the text visual to show zoom scale
        text = scene.visuals.Text('', parent=self.canvas.scene, color='white', bold=True, font_size=16)
        text.pos = 60, 60
        return text

    def on_timer(self, event):
        self.zoom_text.color = [1,1,1,float((7-event.iteration) % 8)/8]
        self.canvas.update()

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
            rolling can be performed using Q and E.'''
        cam1 = scene.cameras.FlyCamera(parent=self.view.scene, fov=fov, name='Fly')

        # 3D camera class that orbits around a center point while maintaining a view on a center point.
        cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=fov,
                                            name='Turntable')
        cam3 = scene.cameras.ArcballCamera(parent=self.view.scene, fov=fov, name='Arcball')
        return cam1, cam2, cam3

    def on_mouse_wheel(self, event):
        self.zoom_size += event.delta[1]
        self.zoom_text.text = 'X %s' % round(self.zoom_size, 1)
        self.zoom_text.show = True
        self.zoom_timer.start(interval=0.2, iterations=8)

    # @canvas.events.key_press.connect
    def on_key_press(self, event):

        if self.view is None:
            return

    # We could move these keypress functionality to the side_panel
    '''    if event.text == '1':
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
        # elif event.text == '4':
        #     if self.volume1.method in ['mip', 'iso']:
        #         cmap = self.opaque_cmap = next(self.opaque_cmaps)
        #     else:
        #         cmap = self.translucent_cmap  = next(self.translucent_cmaps)
        #     self.volume1.cmap = cmap

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
    #        print("Volume scale: %d" % result)'''
