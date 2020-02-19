import sys

import numpy as np

from vispy import scene
from .axes import AxesVisual3D
from ..utils import NestedSTTransform

from matplotlib.colors import ColorConverter

from glue.config import settings

rgb = ColorConverter().to_rgb

LIMITS_PROPS = [coord + attribute for coord in 'xyz' for attribute in ['_min', '_max', '_stretch']]


class VispyWidgetHelper(object):

    def __init__(self, parent=None, viewer_state=None):

        # Prepare Vispy canvas. We set the depth_size to 24 to avoid issues
        # with isosurfaces on MacOS X
        self.canvas = scene.SceneCanvas(keys=None, show=False,
                                        config={'depth_size': 24},
                                        bgcolor=rgb(settings.BACKGROUND_COLOR))

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

        # We need to call render here otherwise we'll later encounter an OpenGL
        # program validation error.
        # self.canvas.render()

        self.viewer_state = viewer_state
        try:
            self.viewer_state.add_callback('*', self._update_from_state, as_kwargs=True)
        except TypeError:  # glue-core >= 0.11
            self.viewer_state.add_global_callback(self._update_from_state)
        self._update_from_state(force=True)

    def _update_appearance_from_settings(self):
        self.canvas.bgcolor = rgb(settings.BACKGROUND_COLOR)
        self.axis.axis_color = rgb(settings.FOREGROUND_COLOR)
        self.axis.tick_color = rgb(settings.FOREGROUND_COLOR)
        self.axis.label_color = rgb(settings.FOREGROUND_COLOR)

    def add_data_visual(self, visual):
        self.limit_transforms[visual] = NestedSTTransform()
        self._update_limits()
        visual.transform = self.limit_transforms[visual]
        self.view.add(visual)

    def _update_from_state(self, force=False, **props):

        if force or 'visible_axes' in props:
            self._toggle_axes()

        if force or 'perspective_view' in props:
            self._toggle_perspective()

        if force or any(key in props for key in ('x_att', 'y_att', 'z_att')):
            self._update_attributes()

        if force or any(key in props for key in ('x_stretch', 'y_stretch',
                                                 'z_stretch', 'native_aspect')):
            self._update_stretch()

        if force or any(p in props for p in LIMITS_PROPS) or 'native_aspect' in props:
            self._update_limits()

        self.canvas.update()

    def _toggle_axes(self):
        if self.viewer_state.visible_axes:
            self.axis.parent = self.view.scene
        else:
            self.axis.parent = None

    def _toggle_perspective(self):
        if self.viewer_state.perspective_view:
            self.view.camera.fov = 30
            self.axis.tick_font_size = 28
            self.axis.axis_font_size = 35
        else:
            self.view.camera.fov = 0
            self.axis.tick_font_size = 6
            self.axis.axis_font_size = 8

    def _update_attributes(self):
        if self.viewer_state.x_att is not None:
            self.axis.xlabel = self.viewer_state.x_att.label
        if self.viewer_state.y_att is not None:
            self.axis.ylabel = self.viewer_state.y_att.label
        if self.viewer_state.z_att is not None:
            self.axis.zlabel = self.viewer_state.z_att.label

    def _update_stretch(self):
        self.scene_transform.scale = (self.viewer_state.x_stretch * self.viewer_state.aspect[0],
                                      self.viewer_state.y_stretch * self.viewer_state.aspect[1],
                                      self.viewer_state.z_stretch * self.viewer_state.aspect[2])

    def _update_limits(self):

        dx = self.viewer_state.x_max - self.viewer_state.x_min
        sx = (np.inf if dx == 0 else 2. / dx *
              self.viewer_state.x_stretch * self.viewer_state.aspect[0])

        dy = self.viewer_state.y_max - self.viewer_state.y_min
        sy = (np.inf if dy == 0 else 2. / dy *
              self.viewer_state.y_stretch * self.viewer_state.aspect[1])

        dz = self.viewer_state.z_max - self.viewer_state.z_min
        sz = (np.inf if dz == 0 else 2. / dz *
              self.viewer_state.z_stretch * self.viewer_state.aspect[2])

        scale = [sx, sy, sz]

        translate = [-0.5 * (self.viewer_state.x_min + self.viewer_state.x_max) * scale[0],
                     -0.5 * (self.viewer_state.y_min + self.viewer_state.y_max) * scale[1],
                     -0.5 * (self.viewer_state.z_min + self.viewer_state.z_max) * scale[2]]

        for visual in self.limit_transforms:
            self.limit_transforms[visual].scale = scale
            self.limit_transforms[visual].translate = translate

        self.axis.xlim = self.viewer_state.x_min, self.viewer_state.x_max
        self.axis.ylim = self.viewer_state.y_min, self.viewer_state.y_max
        self.axis.zlim = self.viewer_state.z_min, self.viewer_state.z_max
