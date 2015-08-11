from __future__ import absolute_import, division, print_function
from glue.config import qt_client, data_factory, link_function
from glue.qt.widgets.data_viewer import DataViewer
from glue.external.qt import QtGui
from itertools import cycle
import numpy as np
import vispy
from vispy import app, scene, io
from vispy.color import get_colormaps, BaseColormap


class VispyWidget(QtGui.QWidget):
# Prepare canvas
    def __init__(self, parent=None):
        super(VispyWidget, self).__init__(parent=parent)
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
        self.canvas.measure_fps()
        self.data = None

    def set_data(self, data):
        self.data = data

    def set_canvas(self):
        # Set all nan to zero for display
        if self.data is None:
            return
        vol1 = np.nan_to_num(np.array(self.data))

        # Prepare canvas
        # Set up a viewbox to display the image with interactive pan/zoom
        view = self.canvas.central_widget.add_view()

        # Set whether we are emulating a 3D texture
        emulate_texture = False

        # Create the volume visuals, only one is visible
        volume1 = scene.visuals.Volume(vol1, parent=view.scene, threshold=0.1,
                                       emulate_texture=emulate_texture)
        # volume1.transform = scene.STTransform(translate=(64, 64, 0))

        # Create two cameras (1 for firstperson, 3 for 3d person)
        fov = 60.
        cam1 = scene.cameras.FlyCamera(parent=view.scene, fov=fov, name='Fly')
        cam2 = scene.cameras.TurntableCamera(parent=view.scene, fov=fov,
                                             name='Turntable')
        cam3 = scene.cameras.ArcballCamera(parent=view.scene, fov=fov, name='Arcball')
        view.camera = cam2  # Select turntable at firstate_texture=emulate_texture)

    def set_colormap(self):
        # Setup colormap iterators
        opaque_cmaps = cycle(get_colormaps())
        translucent_cmaps = cycle([TransFire(), TransGrays()])
        opaque_cmap = next(opaque_cmaps)
        translucent_cmap = next(translucent_cmaps)
        result = 1

   # Implement key presses
   #@canvas.events.key_press.connect
    def on_key_press(event):
        # result =1 # invoke every press...
        global opaque_cmap, translucent_cmap, result
        if event.text == '1':
            cam_toggle = {cam1: cam2, cam2: cam3, cam3: cam1}
            view.camera = cam_toggle.get(view.camera, cam2)
    #        print(view.camera.name + ' camera')
        elif event.text == '2':
            methods = ['mip', 'translucent', 'iso', 'additive']
            method = methods[(methods.index(volume1.method) + 1) % 4]
            print("Volume render method: %s" % method)
            cmap = opaque_cmap if method in ['mip', 'iso'] else translucent_cmap
            volume1.method = method
            volume1.cmap = cmap
        elif event.text == '3':
            volume1.visible = not volume1.visible
        elif event.text == '4':
            if volume1.method in ['mip', 'iso']:
                cmap = opaque_cmap = next(opaque_cmaps)
            else:
                cmap = translucent_cmap = next(translucent_cmaps)
            volume1.cmap = cmap

        elif event.text == '0':
            cam1.set_range()
            cam3.set_range()
        elif event.text != '' and event.text in '[]':
            s = -0.025 if event.text == '[' else 0.025
            volume1.threshold += s
            th = volume1.threshold if volume1.visible else volume2.threshold
    #        print("Isosurface threshold: %0.3f" % th)
        # Add zoom out functionality for the third dimension
        elif event.text != '' and event.text in '=-':
            z = -1 if event.text == '-' else +1
            result += z
            if result > 0:
                volume1.transform = scene.STTransform(scale=(1, 1, result))
            else:
                result = 1
    #        print("Volume scale: %d" % result)

# create colormaps that work well for translucent and additive volume rendering
class TransFire(BaseColormap):
    glsl_map = """
        vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
        }
        """

class TransGrays(BaseColormap):
    glsl_map = """
        vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
        }
        """

class Mygluewidget(DataViewer):
    LABEL = 'astro-vispy'
    def __init__(self, session, parent=None):
        super(Mygluewidget, self).__init__(session, parent=parent)
        # As long as vispy is using Qt as its backend, then Canvas.native refers to the underlying QGLWidget. While QGLWidget inherits from QWidget.
        self.my_widget = VispyWidget()
        self.setCentralWidget(self.my_widget.canvas.native)

    def add_data(self, data):
        self.my_widget.set_data(data['PRIMARY'])
        self.my_widget.set_canvas()
        #Render the scene to an offscreen buffer and return the image array.
        self.my_widget.canvas.render()
        return True

from glue.config import qt_client
qt_client.add(Mygluewidget)

