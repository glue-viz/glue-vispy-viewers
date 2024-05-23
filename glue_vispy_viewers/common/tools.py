import os

from glue.viewers.common.tool import Tool, CheckableTool

from glue.config import viewer_tool

from vispy import app


ROTATE_ICON = os.path.join(os.path.dirname(__file__), 'glue_rotate.png')


@viewer_tool
class ResetTool(Tool):

    icon = 'glue_home'
    tool_id = 'vispy:reset'
    action_text = 'Reset the view'
    tool_tip = 'Reset the view'

    def activate(self):
        self.viewer._vispy_widget.view.camera.reset()
        self.viewer._vispy_widget._toggle_perspective()
        self.viewer.state.reset_limits()


@viewer_tool
class RotateTool(CheckableTool):

    icon = ROTATE_ICON
    tool_id = 'vispy:rotate'
    action_text = 'Continuously rotate view'
    tool_tip = 'Start/Stop rotation'

    timer = None

    def activate(self):
        if self.timer is None:
            self.timer = app.Timer(connect=self.rotate)
        self.timer.start(0.1)

    def deactivate(self):
        self.timer.stop()

    def rotate(self, event):
        self.viewer._vispy_widget.view.camera.azimuth -= 1.  # set speed as constant first
