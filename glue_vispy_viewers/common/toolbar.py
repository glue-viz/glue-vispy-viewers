"""
This file will replace current toolbar and tools
all button functions will be implemented as a tool function
"""


from __future__ import absolute_import, division, print_function

from glue.viewers.common.qt.toolbar import BasicToolbar

from .selection_tools import VispyMouseMode


class VispyViewerToolbar(BasicToolbar):

    def __init__(self, viewer=None):
        BasicToolbar.__init__(self, viewer)
        self._vispy_widget = viewer._vispy_widget
        self.canvas = self._vispy_widget.canvas

    def activate_tool(self, mode):
        if isinstance(mode, VispyMouseMode):
            self._vispy_widget.canvas.events.mouse_press.connect(mode.press)
            self._vispy_widget.canvas.events.mouse_release.connect(mode.release)
            self._vispy_widget.canvas.events.mouse_move.connect(mode.move)
            self.disable_camera_events()
        super(VispyViewerToolbar, self).activate_tool(mode)

    def deactivate_tool(self, mode):
        if isinstance(mode, VispyMouseMode):
            self._vispy_widget.canvas.events.mouse_press.disconnect(mode.press)
            self._vispy_widget.canvas.events.mouse_release.disconnect(mode.release)
            self._vispy_widget.canvas.events.mouse_move.disconnect(mode.move)
            self.enable_camera_events()
        super(VispyViewerToolbar, self).deactivate_tool(mode)

    @property
    def camera(self):
        return self._vispy_widget.view.camera

    def enable_camera_events(self):
        self.camera._viewbox.events.mouse_move.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_press.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_release.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_wheel.connect(self.camera.viewbox_mouse_event)

    def disable_camera_events(self):
        self.camera._viewbox.events.mouse_move.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_press.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_release.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_wheel.disconnect(self.camera.viewbox_mouse_event)
