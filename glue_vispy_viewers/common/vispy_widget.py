from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from ..extern.vispy import scene
from .axes import AxesVisual3D

from qtpy import QtWidgets
from glue.utils.qt import get_qapp

from glue.config import settings
from glue.external.echo import CallbackProperty, add_callback

from glue.utils import nonpartial

from matplotlib.colors import ColorConverter

rgb = ColorConverter().to_rgb


class VispyWidget(QtWidgets.QWidget):

    visible_axes = CallbackProperty()
    perspective_view = CallbackProperty()
    clip_data = CallbackProperty()
    clip_limits = CallbackProperty()

    def _update_appearance_from_settings(self):
        self.canvas.bgcolor = rgb(settings.BACKGROUND_COLOR)
        self.axis.color = rgb(settings.FOREGROUND_COLOR)

    def __init__(self, parent=None):

        super(VispyWidget, self).__init__(parent=parent)

        # Prepare Vispy canvas. We set the depth_size to 24 to avoid issues
        # with isosurfaces on MacOS X
        self.canvas = scene.SceneCanvas(keys=None, show=False,
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

        self.axis = AxesVisual3D(axis_color=fc, tick_color=fc, text_color=fc,
                                 tick_width=1, minor_tick_length=2,
                                 major_tick_length=4, axis_width=0,
                                 tick_label_margin=10, axis_label_margin=25,
                                 tick_font_size=6, axis_font_size=8,
                                 view=self.view,
                                 transform=self.scene_transform)

        # Create a turntable camera. For now, this is the only camerate type
        # we support, but if we support more in future, we should implement
        # that here

        # Orthographic perspective view as default
        self.view.camera = scene.cameras.TurntableCamera(parent=self.view.scene,
                                                         fov=0., distance=4.0)

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

    def _toggle_axes(self):
        if self.visible_axes:
            self.axis.parent = self.view.scene
        else:
            self.axis.parent = None
        self.canvas.update()

    def _toggle_perspective(self):
        if self.perspective_view:
            self.view.camera.fov = 30
            self.axis.tick_font_size = 28
            self.axis.axis_font_size = 35
        else:
            self.view.camera.fov = 0
            self.axis.tick_font_size = 6
            self.axis.axis_font_size = 8

    def add_data_visual(self, visual):
        self.limit_transforms[visual] = scene.STTransform()
        visual.transform = self.limit_transforms[visual]
        self.view.add(visual)

    def _update_attributes(self):
        self.axis.xlabel = self.options.x_att.label
        self.axis.ylabel = self.options.y_att.label
        self.axis.zlabel = self.options.z_att.label

    def _update_stretch(self, *stretch):
        self.scene_transform.scale = stretch
        self._update_limits()

    def _update_limits(self):

        if len(self.limit_transforms) == 0:
            return

        if (self.options.x_min is None or self.options.x_max is None or
            self.options.y_min is None or self.options.y_max is None or
            self.options.z_min is None or self.options.z_max is None):
            raise Exception("We should never get here because if any data is "
                            "present, the limits should be set")

        scale = [2 / (self.options.x_max - self.options.x_min) * self.options.x_stretch * self.options.aspect[0],
                 2 / (self.options.y_max - self.options.y_min) * self.options.y_stretch * self.options.aspect[1],
                 2 / (self.options.z_max - self.options.z_min) * self.options.z_stretch * self.options.aspect[2]]

        translate = [-0.5 * (self.options.x_min + self.options.x_max) * scale[0],
                     -0.5 * (self.options.y_min + self.options.y_max) * scale[1],
                     -0.5 * (self.options.z_min + self.options.z_max) * scale[2]]

        for visual in self.limit_transforms:
            self.limit_transforms[visual].scale = scale
            self.limit_transforms[visual].translate = translate

        self.axis.xlim = self.options.x_min, self.options.x_max
        self.axis.ylim = self.options.y_min, self.options.y_max
        self.axis.zlim = self.options.z_min, self.options.z_max

        self.clip_limits = (self.options.x_min, self.options.x_max,
                            self.options.y_min, self.options.y_max,
                            self.options.z_min, self.options.z_max)

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
