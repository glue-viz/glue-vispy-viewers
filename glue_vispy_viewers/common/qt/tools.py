import os

from qtpy import QtGui, compat

from glue.viewers.common.tool import Tool, CheckableTool

from glue.config import viewer_tool

from vispy import app, io

RECORD_START_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_start.png')
RECORD_STOP_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_stop.png')


@viewer_tool
class SaveTool(Tool):

    icon = 'glue_filesave'
    tool_id = 'vispy:save'
    action_text = 'Save the figure to a file'
    tool_tip = 'Save the figure to a file'

    def activate(self):
        outfile, file_filter = compat.getsavefilename(caption='Save File',
                                                      filters='PNG Files (*.png);;'
                                                              'JPEG Files (*.jpeg);;'
                                                              'TIFF Files (*.tiff);;',
                                                      selectedfilter='PNG Files (*.png);;')

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
class RecordTool(CheckableTool):

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

        # pop up a window for file saving
        outfile, file_filter = compat.getsavefilename(caption='Save Animation',
                                                      filters='GIF Files (*.gif);;')

        # if outfile is not set, the user cancelled
        if outfile:
            import imageio
            self.set_icon(RECORD_STOP_ICON)
            self.writer = imageio.get_writer(outfile)
            self.record_timer.start(0.1)

    def deactivate(self):

        self.record_timer.stop()
        if self.writer is not None:
            self.writer.close()
        self.set_icon(RECORD_START_ICON)

    def set_icon(self, icon):
        self.viewer.toolbar.actions[self.tool_id].setIcon(QtGui.QIcon(icon))

    def record(self, event):
        im = self.viewer._vispy_widget.canvas.render()
        self.writer.append_data(im)
