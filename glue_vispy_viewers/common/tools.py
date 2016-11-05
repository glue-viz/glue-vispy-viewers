from __future__ import absolute_import, division, print_function

import os

import numpy as np
from ..extern.vispy import app, scene, io

from qtpy import QtGui, compat
from qtpy.QtWidgets import QMessageBox

from glue.viewers.common.qt.tool import Tool, CheckableTool

from glue.core import Data
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState
from glue.config import settings, viewer_tool


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
            if not '.' in outfile:
                outfile += '.png'
            io.write_png(outfile, img)


@viewer_tool
class RecordTool(CheckableTool):

    icon = RECORD_START_ICON
    tool_id = 'vispy:record'
    action_text = 'Record an animation'
    tool_tip = 'Start/Stop the recording'

    def __init__(self, viewer):
        super(RecordTool, self).__init__(viewer=viewer)
        self.record_timer = app.Timer(connect=self.record)
        self.writer = None
        try:
            import imageio
        except:
            self.tool_tip = 'The imageio package is required for recording'
            self.disable()

    def activate(self):

        # pop up a window for file saving
        outfile, file_filter = compat.getsavefilename(caption='Save Animation',
                                                      filters='GIF Files (*.gif);;')
        # This indicates that the user cancelled
        if outfile:
            self.icon = QtGui.QIcon(RECORD_STOP_ICON)
            # self.record_action.setIcon(QtGui.QIcon(RECORD_STOP_ICON))
            import imageio
            self.writer = imageio.get_writer(outfile)
            self.record_timer.start(0.1)
        else:
            self.deactivate()

            # TODO: this should be added later
            # self.record_action.blockSignals(True)
            # self.record_action.setChecked(False)
            # self.record_action.blockSignals(False)

    def deactivate(self):
        self.record_timer.stop()
        self.icon = QtGui.QIcon(RECORD_START_ICON)
        if self.writer is not None:
            self.writer.close()

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
