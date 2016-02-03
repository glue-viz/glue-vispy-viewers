from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app
from matplotlib.colors import ColorConverter

from .colors import get_translucent_cmap
from .volume_visual import MultiVolume

__all__ = ['QtVispyWidget']


GRAYS = get_translucent_cmap(1, 1, 1)
COLOR_CONVERTER = ColorConverter()

class QtVispyWidget(QtGui.QWidget):

    def __init__(self, parent=None):

        super(QtVispyWidget, self).__init__(parent=parent)

        self._subset_changed = False

        # Prepare canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=False, always_on_top=False)
        self.canvas.measure_fps()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.canvas.central_widget.add_view()
        self.view.border_color = 'red'
        self.view.parent = self.canvas.scene

        # Set whether we are emulating a 3D texture. This needs to be enabled
        # as a workaround on Windows otherwise VisPy crashes.
        self.emulate_texture = (sys.platform == 'win32' and
                                sys.version_info[0] < 3)

        self.data = None
        self.axes_names = None
        self._current_array = None

        self.vol_visual = None
        self.zoom_size = 0
        self.zoom_text_visual = self.add_text_visual()
        self.zoom_timer = app.Timer(0.2, connect=self.on_timer, start=False)
        self.cube_diagonal = 0.0
        self.ori_distance = 0.0

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.widget_axis_scale = [1, 1, 1]

        # Set up cameras
        self.flyCamera, self.turntableCamera = self.set_cam()
        self.view.camera = self.turntableCamera  # Select turntable at firstate_texture=emulate_texture)

        # Set up default colormap
        # self.color_map = get_colormap('grays')

        # Connect events
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.resize.connect(self.on_resize)

        self._shown_data = None

        self._camera_updated = False

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if data is None:
            self._data = data
        else:
            self._data = data
            first_data = data[data.components[0]]
            self.cube_diagonal = np.sqrt(first_data.shape[0] ** 2 +
                                         first_data.shape[1] ** 2 +
                                         first_data.shape[2] ** 2)
            self.ori_distance = self.cube_diagonal / (np.tan(np.radians(60)))
            self.options_widget.set_valid_components([c.label for c in data.component_ids()])
            self.options_widget.set_axis_names([data.coords.axis_label(idx) for idx in range(3)][::-1])
            self._refresh()

    @property
    def component(self):
        if self.data is None:
            return None
        else:
            return self.data[self.options_widget.visible_component]

    def _refresh(self):
        """
        This method can be called if the options widget is updated.
        """

        if self.data is None:
            return

        stretch_scale = self.options_widget.stretch
        stretch_tran = [-0.5 * stretch_scale[idx] * self.component.shape[2-idx] for idx in range(3)]

        if self.vol_visual is not None:

            self.vol_visual.transform.translate = stretch_tran
            self.vol_visual.transform.scale = stretch_scale

            array = self.component

            if array is not self._current_array[0] or (self.options_widget.cmin, self.options_widget.cmax) != self._current_array[1]:
                self._current_array = (array,
                                       (self.options_widget.cmin,
                                        self.options_widget.cmax))
                array = np.nan_to_num(array)
                self._update_clim(array)
                clim = float(self.options_widget.cmin), float(self.options_widget.cmax)
                self.vol_visual.set_volume('data', array, clim, self.options_widget.cmap)

            if self._subset_changed:
                clim = float(self.options_widget.cmin), float(self.options_widget.cmax)
                for subset in self.subsets:
                    rgb = COLOR_CONVERTER.to_rgb(subset['color'])
                    cmap = get_translucent_cmap(*rgb)
                    subset_data = array.copy()
                    subset_data[~subset['mask']] = clim[0]
                    self.vol_visual.set_volume(subset['label'], subset_data, clim, cmap)

        if self._camera_updated:
            self.canvas.update()
        else:
            self._update_camera()

    def _update_camera(self):

        self._camera_updated = True

        if self.options_widget.view_mode == "Normal View Mode":
            self.view.camera = self.turntableCamera
            self.turntableCamera.distance = self.ori_distance
            self.turntableCamera.scale_factor = self.cube_diagonal
        else:
            self.view.camera = self.flyCamera

        self.canvas.update()

    def _update_data_weight(self):
        self.vol_visual.set_weight('data', float(self.options_widget.data_weight) / 100.)
        self.canvas.update()

    def _update_clim(self, array):

        if self.options_widget.cmin == 'auto':
            self.options_widget.cmin = "%.4g" % np.min(array)

        if self.options_widget.cmax == 'auto':
            self.options_widget.cmax = "%.4g" % np.max(array)

    def set_subsets(self, subsets):
        self._subset_changed = True
        self.subsets = subsets
        self._refresh()

    def add_volume_visual(self):

        # TODO: need to implement the visualiation of the subsets in this method

        # Create the volume visual and give default settings
        vol_data = self.component
        self._current_array = (vol_data,
                               (self.options_widget.cmin,
                                self.options_widget.cmax))
        vol_data = np.nan_to_num(vol_data)
        self._update_clim(vol_data)

        vol_visual = MultiVolume(parent=self.view.scene, threshold=0.1,
                                 emulate_texture=self.emulate_texture)

        clim=(float(self.options_widget.cmin),
              float(self.options_widget.cmax))

        vol_visual.set_volume('data', vol_data, clim, self.options_widget.cmap)

        trans = (-vol_data.shape[2]/2, -vol_data.shape[1]/2, -vol_data.shape[0]/2)
        _axis_scale = (vol_data.shape[2], vol_data.shape[1], vol_data.shape[0])
        vol_visual.transform = scene.STTransform(translate=trans)

        self.axis.transform = scene.STTransform(translate=trans, scale=_axis_scale)

        self.vol_visual = vol_visual
        self.widget_axis_scale = self.axis.transform.scale

        self._update_camera()

    def add_text_visual(self):
        # Create the text visual to show zoom scale
        text = scene.visuals.Text('', parent=self.canvas.scene, color='white', bold=True, font_size=16)
        text.pos = [40, self.canvas.size[1]-40]
        return text

    def on_timer(self, event):
        self.zoom_text_visual.color = [1, 1, 1, float((7-event.iteration) % 8)/8]
        self.canvas.update()

    def on_resize(self, event):
        self.zoom_text_visual.pos = [40, self.canvas.size[1] - 40]

    def set_cam(self, cam_fov=60):
        # Create two cameras (1 for firstperson, 3 for 3d person)
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
        cam1 = scene.cameras.FlyCamera(parent=self.view.scene, fov=cam_fov, name='Fly')

        # 3D camera class that orbits around a center point while maintaining a view on a center point.
        cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=cam_fov,
                                             name='Turntable')
        return cam1, cam2

    def on_mouse_wheel(self, event):
        if self.view.camera is self.turntableCamera:
            if self.view.camera.distance is None:
                self.view.camera.distance = 10.0
            self.zoom_size = self.ori_distance / self.view.camera.distance
            # self.zoom_size += event.delta[1]
            self.zoom_text_visual.text = 'X %s' % round(self.zoom_size, 1)
            self.zoom_timer.start(interval=0.2, iterations=8)
        # TODO: add a bound for fly_mode mouse_wheel
