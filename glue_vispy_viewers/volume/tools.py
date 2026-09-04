from qtpy import compat

from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_vispy_viewers.volume.cut_plane_export import render_cut_plane_image

from vispy import io


__all__ = ['CutPlaneExportTool']


@viewer_tool
class CutPlaneExportTool(Tool):
    icon = 'glue_filesave'
    tool_id = 'save:exportplane'
    action_text = 'Export the cut plane image'
    tool_tip = 'Export the cut plane image'

    def activate(self):
        outfile, file_filter = compat.getsavefilename(caption='Save File',
                                                      filters='PNG Files (*.png);;'
                                                              'JPEG Files (*.jpeg);;'
                                                              'TIFF Files (*.tiff);;',
                                                      selectedfilter='PNG Files (*.png);;')

        # This indicates that the user cancelled
        if not outfile:
            return
        img = render_cut_plane_image(self.viewer.state,
                                     self.viewer._vispy_widget._multivol) 
        try:
            file_filter = str(file_filter).split()[0]
            io.imsave(outfile, img, format=file_filter)
        except ImportError:
            # TODO: give out a window to notify that only .png file format is supported
            if '.' not in outfile:
                outfile += '.png'
            io.write_png(outfile, img)
