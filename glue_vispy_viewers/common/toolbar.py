"""
This file will replace current toolbar and tools
all button functions will be implemented as a tool function
"""

from .selection_tools import VispyMouseMode


class VispyViewerToolbarMixin:

    def _enable_tool_interactions(self, mode):
        if isinstance(mode, VispyMouseMode):
            self._vispy_widget.canvas.events.mouse_press.connect(mode.press)
            self._vispy_widget.canvas.events.mouse_release.connect(mode.release)
            self._vispy_widget.canvas.events.mouse_move.connect(mode.move)
            self.disable_camera_events()

    def _disable_tool_interactions(self, mode):
        if isinstance(mode, VispyMouseMode):
            self._vispy_widget.canvas.events.mouse_press.disconnect(mode.press)
            self._vispy_widget.canvas.events.mouse_release.disconnect(mode.release)
            self._vispy_widget.canvas.events.mouse_move.disconnect(mode.move)
            self.enable_camera_events()

    @property
    def camera(self):
        return self._vispy_widget.view.camera

    def enable_camera_events(self):
        self.camera.interactive = True

    def disable_camera_events(self):
        self.camera.interactive = False

    @property
    def _vispy_widget(self):
        return self.viewer._vispy_widget

    @property
    def canvas(self):
        return self._vispy_widget.canvas
