from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from ..extern.vispy import scene
from ..extern.vispy.geometry import create_cube

try:
    from glue.external.qt import QtGui as QtWidgets, get_qapp
except ImportError:
    from qtpy import QtWidgets
    from glue.utils.qt import get_qapp

from glue.config import settings
from glue.external.echo import CallbackProperty, add_callback

from glue.utils import nonpartial

from matplotlib.colors import ColorConverter

rgb = ColorConverter().to_rgb

from ..extern.vispy.visuals.transforms import STTransform


class VispyWidget(QtWidgets.QWidget):

    visible_axes = CallbackProperty()
    perspective_view = CallbackProperty()

    def _update_appearance_from_settings(self):
        self.canvas.bgcolor = rgb(settings.BACKGROUND_COLOR)
        self.axis.color = rgb(settings.FOREGROUND_COLOR)

    def __init__(self, parent=None):

        super(VispyWidget, self).__init__(parent=parent)

        # Prepare Vispy canvas. We set the depth_size to 24 to avoid issues
        # with isosurfaces on MacOS X
        self.canvas = scene.SceneCanvas(keys='interactive', show=False,
                                        config={'depth_size': 24}, bgcolor=rgb(settings.BACKGROUND_COLOR))

        # Set up a viewbox
        self.view = self.canvas.central_widget.add_view()
        self.view.parent = self.canvas.scene

        # Set whether we are emulating a 3D texture. This needs to be enabled
        # as a workaround on Windows otherwise VisPy crashes.
        self.emulate_texture = (sys.platform == 'win32' and
                                sys.version_info[0] < 3)

        self.scene_transform = scene.STTransform()
        self.limit_transforms = {}

        fc = rgb(settings.FOREGROUND_COLOR)

        # Add a 3D cube to show us the unit cube. The 1.001 factor is to make
        # sure that the grid lines are not 'hidden' by volume renderings on the
        # front side due to numerical precision.
        vertices, filled_indices, outline_indices = create_cube()
        self.axis = scene.visuals.Mesh(vertices['position'],
                                       outline_indices,
                                       color=fc, mode='lines')
        self.axis.transform = self.scene_transform
        self.view.add(self.axis)

        # add the axis visual from Vispy library, with 2D ticks and labels, more refer to:
        # https://github.com/vispy/vispy/blob/959fe5643ec9d717f9f01ba97552ec1c1668ec04/vispy/visuals/axis.py
        # TODO: move this 3d axis into a subclass, set domain as data shape, add coordinate labels
        # TODO: tick text color as foreground color
        self.xax = scene.visuals.Axis(pos=[[-1.0, -1.0], [1.0, -1.0]], domain=(5., 10.), tick_direction=(0, -1),
                         font_size=10, axis_color=fc, tick_color=fc, text_color=fc,
                         parent=self.view.scene)

        self.yax = scene.visuals.Axis(pos=[[-1.0, -1.0], [-1.0, 1.0]], tick_direction=(-1, 0),
                         font_size=10, axis_color=fc, tick_color=fc, text_color=fc,
                         parent=self.view.scene)

        self.zax = scene.visuals.Axis(pos=[[-1.0, -1.0], [-1.0, 1.0]], tick_direction=(-1, 0),
                         font_size=10, axis_color=fc, tick_color=fc, text_color=fc,
                         parent=self.view.scene)

        self.xytr = STTransform()
        self.xytr.translate = [0., 0., -1.]

        self.xax.transform = self.xytr
        self.yax.transform = self.xytr

        # zax is the 180 rotation of yax
        self.ztr = STTransform()
        try:
            self.ztr = self.ztr.as_matrix()
        except AttributeError:   # Vispy <= 0.4
            self.ztr = self.ztr.as_affine()

        self.ztr.rotate(180, (0, 1, 1))
        self.ztr.translate((-2., -1., 0.))
        self.zax.transform = self.ztr

        # Create a turntable camera. For now, this is the only camerate type
        # we support, but if we support more in future, we should implement
        # that here

        # Orthographic perspective view as default
        self.view.camera = scene.cameras.TurntableCamera(parent=self.view.scene, fov=0., distance=4.0)

        # Add the native canvas widget to this widget
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas.native)
        self.setLayout(layout)

        # We need to call render here otherwise we'll later encounter an OpenGL
        # program validation error.
        self.canvas.render()

        # Set up callbacks
        add_callback(self, 'visible_axes', nonpartial(self._toggle_axes))
        add_callback(self, 'perspective_view', nonpartial(self._toggle_perspective))

    # TODO: how to get data here?
    def update_axis_label(self, data):
        # data object
        label = []
        tick_value = []
        if data.coords:
            # TODO: think about 4th dim
            for i in range(data.ndim):
                label.append(data.coords.axis_label(i))  # ['Vopt', 'Declination', 'Right Ascension']
                tick_value.append(data._world_component_ids[label[i]])
            self.xax.domain = tick_value[0]
            self.yax.domain = tick_value[1]
            self.zax.domain = tick_value[2]

    def _toggle_axes(self):
        if self.visible_axes:
            self.axis.parent = self.view.scene
        else:
            self.axis.parent = None
        self.canvas.update()

    def _toggle_perspective(self):
        if self.perspective_view:
            self.view.camera.fov = 60
        else:
            self.view.camera.fov = 0

    def add_data_visual(self, visual):
        self.limit_transforms[visual] = scene.STTransform()
        visual.transform = self.limit_transforms[visual]
        self.view.add(visual)

    def _update_stretch(self, *stretch):
        self.scene_transform.scale = stretch

        # set stretch for 3d axis here
        self.xytr.scale = stretch
        self.xytr.translate = [0., 0., -stretch[2]]

        # self.ztr.scale will accumulate with previous settings, so we need reset
        self.ztr.reset()
        self.ztr.rotate(180, (0, 1, 1))
        self.ztr.translate((-2., -1., 0.))
        self.ztr.scale(stretch)
        self._update_limits()

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
        # update the cam.fov with checkbox
        self._toggle_perspective()


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
