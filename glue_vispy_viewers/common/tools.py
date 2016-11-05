from __future__ import absolute_import, division, print_function

import os

from qtpy import QtGui, compat
from glue.viewers.common.qt.tool import Tool, CheckableTool
from glue.config import viewer_tool

from ..extern.vispy import app, io


RECORD_START_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_start.png')
RECORD_STOP_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_stop.png')
ROTATE_ICON = os.path.join(os.path.dirname(__file__), 'glue_rotate.png')


@viewer_tool
class SaveTool(Tool):

    icon = 'glue_filesave'
    tool_id = 'vispy:save'
    action_text = 'Save the figure'
    tool_tip = 'Save the figure'
    shortcut = 'Ctrl+Shift+S'

    def activate(self):
        outfile, file_filter = compat.getsavefilename(caption='Save File',
                                                      filters='PNG Files (*.png);;'
                                                              'JPEG Files (*.jpeg);;'
                                                              'TIFF Files (*.tiff);;')

        # This indicates that the user cancelled
        if not outfile:
            return
        img = self.viewer._vispy_widget.canvas.render()
        try:
            file_filter = str(file_filter).split()[0]
            io.imsave(outfile, img, format=file_filter)
        except ImportError:
            # TODO: give out a window to notify that only .png file format is supported
            if '.' not in outfile:
                outfile += '.png'
            io.write_png(outfile, img)


@viewer_tool
class RecordTool(Tool):

    icon = RECORD_START_ICON
    tool_id = 'vispy:record'
    action_text = 'Record an animation'
    tool_tip = 'Start/Stop the recording'

    def __init__(self, viewer):
        super(RecordTool, self).__init__(viewer=viewer)
        self.record_timer = app.Timer(connect=self.record)
        self.writer = None
        self.next_action = 'start'

    def activate(self):

        if self.next_action == 'start':

            # pop up a window for file saving
            outfile, file_filter = compat.getsavefilename(caption='Save Animation',
                                                          filters='GIF Files (*.gif);;')

            # if outfile is not set, the user cancelled
            if outfile:
                import imageio
                self.set_icon(RECORD_STOP_ICON)
                self.writer = imageio.get_writer(outfile)
                self.record_timer.start(0.1)
                self.next_action = 'stop'

        else:

            self.record_timer.stop()
            if self.writer is not None:
                self.writer.close()
            self.set_icon(RECORD_START_ICON)
            self.next_action = 'start'

    def set_icon(self, icon):
        self.viewer.toolbar.actions[self.tool_id].setIcon(QtGui.QIcon(icon))

    def record(self, event):
        im = self.viewer._vispy_widget.canvas.render()
        self.writer.append_data(im)


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
