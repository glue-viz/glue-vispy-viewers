"""
This file will replace current toolbar and tools
all button functions will be implemented as a tool function
"""


from __future__ import absolute_import, division, print_function

import os
from qtpy import QtCore
from qtpy import PYQT5

from glue.icons.qt import get_icon
from glue.utils import nonpartial
from glue.viewers.common.qt.tool import CheckableTool, Tool
from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.viewers.common.qt.toolbar import BasicToolbar

if PYQT5:
    from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
else:
    from matplotlib.backends.backend_qt4 import NavigationToolbar2QT

import os

import numpy as np
from ..extern.vispy import app, scene, io

from qtpy import QtCore, QtWidgets, QtGui
from qtpy.compat import getsavefilename
from glue.config import viewer_tool
from glue.viewers.common.qt.tool import Tool, CheckableTool

from glue.icons.qt import get_icon
from glue.utils import nonpartial

try:
    import imageio
except ImportError:
    print('Imageio package required')

from glue.core import Data
from glue.core.exceptions import IncompatibleAttribute
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState
from glue.core.exceptions import IncompatibleAttribute
from glue.config import settings


RECORD_START_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_start.png')
RECORD_STOP_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_stop.png')
POINT_ICON = os.path.join(os.path.dirname(__file__), 'glue_point.png')
ROTATE_ICON = os.path.join(os.path.dirname(__file__), 'glue_rotate.png')


class SaveTool(Tool):
    def __init__(self, viewer):
        super(SaveTool, self).__init__(viewer=viewer)
        self._vispy_widget = viewer._vispy_widget

        self.icon = get_icon('glue_filesave')
        self.tool_id = 'Save'
        self.action_text = 'Save the figure'
        self.tool_tip = 'Save the figure'
        self.shortcut = 'Ctrl+Shift+S'

    def activate(self):
        outfile, file_filter = getsavefilename(caption='Save File',
                                               filters='PNG Files (*.png);;'
                                                       'JPEG Files (*.jpeg);;'
                                                       'TIFF Files (*.tiff);;')

        # This indicates that the user cancelled
        if not outfile:
            return
        img = self._vispy_widget.canvas.render()
        try:
            file_filter = str(file_filter).split()[0]
            io.imsave(outfile, img, format=file_filter)
        except ImportError:
            # TODO: give out a window to notify that only .png file format is supported
            if not '.' in outfile:
                outfile += '.png'
            io.write_png(outfile, img)


class RecordTool(CheckableTool):

    def __init__(self, viewer):
        super(RecordTool, self).__init__(viewer=viewer)
        self._vispy_widget = viewer._vispy_widget

        self.icon = QtGui.QIcon(RECORD_START_ICON)
        self.tool_id = 'Record'
        self.action_text = 'Record'
        self.tool_tip = 'Start/Stop the record'

        # Add a timer to control the view rotate
        # self.timer = app.Timer(connect=self.rotate)
        self.record_timer = app.Timer(connect=self.record)

        self.writer = None

    def activate(self):
        # pop up a window for file saving
        outfile, file_filter = getsavefilename(caption='Save Animation',
                                               filters='GIF Files (*.gif);;')
        # This indicates that the user cancelled
        if outfile:

            self.icon = QtGui.QIcon(RECORD_STOP_ICON)
            # self.record_action.setIcon(QtGui.QIcon(RECORD_STOP_ICON))
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
        self.writer.close()

    def record(self, event):
        if self.writer is not None:
            im = self._vispy_widget.canvas.render()
            self.writer.append_data(im)
        else:
            # maybe better give an option to let user install the package
            print('imageio module needed!')


class RotateTool(CheckableTool):
    def __init__(self, viewer):
        self._vispy_widget = viewer._vispy_widget

        self.icon = QtGui.QIcon(ROTATE_ICON)
        self.tool_id = 'Rotate'
        self.timer = app.Timer(connect=self.rotate)

    def activate(self):
        self.timer.start(0.1)

    def deactivate(self):
        self.timer.stop()

    def rotate(self, event):
        self._vispy_widget.view.camera.azimuth -= 1.  # set speed as constant first


# tools and toolbar will be divided to another file later
class PatchedElementSubsetState(ElementSubsetState):

    # TODO: apply this patch to the core glue code

    def __init__(self, data, indices):
        super(PatchedElementSubsetState, self).__init__(indices=indices)
        self._data = data

    def to_mask(self, data, view=None):
        if data in self._data:
            return super(PatchedElementSubsetState, self).to_mask(data, view=view)
        else:
            # TODO: should really be IncompatibleDataException but many other
            # viewers don't recognize this.
            raise IncompatibleAttribute()

    def copy(self):
        return PatchedElementSubsetState(self._data, self._indices)


class VispyMouseMode(CheckableTool):
    # this will create an abstract selection mode class to handle mouse events
    # instanced by lasso, rectangle, circular and point mode

    def __init__(self, viewer):
        super(VispyMouseMode, self).__init__(viewer)
        self.selection_origin = (0, 0)
        self._vispy_widget = viewer._vispy_widget

        # Initialize drawing visual
        self.line_pos = []
        self.line = scene.visuals.Line(color=settings.FOREGROUND_COLOR,
                                       width=2, method='agg',
                                       parent=self._vispy_widget.canvas.scene)

    def press(self, event):
        if self.tool_id:
            # do the initiation here
            self.selection_origin = event.pos

    def release(self, event):
        pass

    def move(self, event):
        """
        Draw selection line along dragging mouse
        """
        if event.button == 1 and event.is_dragging and 'Point' not in self.tool_id:
            if 'Lasso' in self.tool_id:
                self.line_pos.append(event.pos)
                self.line.set_data(np.array(self.line_pos))
            else:
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                center = (width / 2. + self.selection_origin[0], height / 2.
                          + self.selection_origin[1], 0)

                if 'Rectangle' in self.tool_id:
                    self.line_pos = self.rectangle_vertice(center, height, width)
                    self.line.set_data(np.array(self.line_pos))

                # TODO: circle does not get shown sometimes
                if 'Circle' in self.tool_id:
                    # create a circle instead of ellipse here
                    radius = (np.abs((width + height) / 4.), np.abs((width + height) / 4.))
                    self.line_pos = self.ellipse_vertice(center, radius=radius,
                                                         start_angle=0.,
                                                         span_angle=360.,
                                                         num_segments=500)
                    self.line.set_data(pos=np.array(self.line_pos), connect='strip')

            self._vispy_widget.canvas.update()

    ''' below are common functions for mousemode tool '''

    def get_visible_data(self):
        visible = []
        # Loop over visible layer artists
        print('self.viewer', self.viewer)
        for layer_artist in self.viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        visual = layer_artist.visual  # we only have one visual for each canvas
        return visible, visual

    def mark_selected(self, mask, visible_data):
        # We now make a subset state. For scatter plots we'll want to use an
        # ElementSubsetState, while for cubes, we'll need to change to a
        # MaskSubsetState.
        subset_state = ElementSubsetState(indices=np.where(mask)[0], data=visible_data[0])

        # We now check what the selection mode is, and update the selection as
        # needed (this is delegated to the correct subset mode).
        mode = EditSubsetMode()
        focus = visible_data[0] if len(visible_data) > 0 else None
        # TODO: get data_collection here
        mode.update(self._data_collection, subset_state, focus_data=focus)

    def lasso_reset(self):
        # Reset lasso
        self.line_pos = []
        self.line.set_data(np.zeros((0, 2)))
        self.line.update()
        self.selection_origin = (0, 0)
        self._vispy_widget.canvas.update()

    def rectangle_vertice(self, center, height, width):
        """
        Borrow from _generate_vertices in vispy/visuals/rectangle.py
        """
        half_height = height / 2.
        half_width = width / 2.

        bias1 = np.ones(4) * half_width
        bias2 = np.ones(4) * half_height

        corner1 = np.empty([1, 3], dtype=np.float32)
        corner2 = np.empty([1, 3], dtype=np.float32)
        corner3 = np.empty([1, 3], dtype=np.float32)
        corner4 = np.empty([1, 3], dtype=np.float32)

        corner1[:, 0] = center[0] - bias1[0]
        corner1[:, 1] = center[1] - bias2[0]
        corner1[:, 2] = 0

        corner2[:, 0] = center[0] + bias1[1]
        corner2[:, 1] = center[1] - bias2[1]
        corner2[:, 2] = 0

        corner3[:, 0] = center[0] + bias1[2]
        corner3[:, 1] = center[1] + bias2[2]
        corner3[:, 2] = 0

        corner4[:, 0] = center[0] - bias1[3]
        corner4[:, 1] = center[1] + bias2[3]
        corner4[:, 2] = 0

        # Get vertices between each corner of the rectangle for border drawing
        vertices = np.concatenate(([[center[0], center[1], 0.]],
                                   [[center[0] - half_width, center[1], 0.]],
                                   corner1,
                                   [[center[0], center[1] - half_height, 0.]],
                                   corner2,
                                   [[center[0] + half_width, center[1], 0.]],
                                   corner3,
                                   [[center[0], center[1] + half_height, 0.]],
                                   corner4,
                                   [[center[0] - half_width, center[1], 0.]]))

        # vertices = np.array(output, dtype=np.float32)
        return vertices[1:, ..., :2]

    def ellipse_vertice(self, center, radius, start_angle, span_angle, num_segments):
        # Borrow from _generate_vertices in vispy/visual/ellipse.py

        if isinstance(radius, (list, tuple)):
            if len(radius) == 2:
                xr, yr = radius
            else:
                raise ValueError("radius must be float or 2 value tuple/list"
                                 " (got %s of length %d)" % (type(radius),
                                                             len(radius)))
        else:
            xr = yr = radius

        start_angle = np.deg2rad(start_angle)

        vertices = np.empty([num_segments + 2, 2], dtype=np.float32)  # Segment as 1000

        # split the total angle into num_segments intances
        theta = np.linspace(start_angle,
                            start_angle + np.deg2rad(span_angle),
                            num_segments + 1)

        # PolarProjection
        vertices[:-1, 0] = center[0] + xr * np.cos(theta)
        vertices[:-1, 1] = center[1] + yr * np.sin(theta)

        # close the curve
        vertices[num_segments + 1] = np.float32([center[0], center[1]])

        return vertices[:-1]


class VispyViewerToolbar(BasicToolbar):

    def __init__(self, vispy_widget=None, parent=None): #parent would be a viewer
        print('vispyviewer toolbar parent is', parent)
        self._vispy_widget = parent._vispy_widget
        self.canvas = parent._vispy_widget.canvas

        BasicToolbar.__init__(self, parent)

        # Set visual preferences
        self.setIconSize(QtCore.QSize(25, 25))

    def setup_default_modes(self):
        save_mode = SaveTool(self.parent())
        self.add_tool(save_mode)

        try:
            import imageio
            record_mode = RecordTool(self.parent())
            self.add_tool(record_mode)
        except ImportError:
            print('Record tool not loaded, imageio package is required')

        rotate_mode = RotateTool(self.parent())
        self.add_tool(rotate_mode)

    def activate_tool(self, mode):
        if isinstance(mode, VispyMouseMode):
            # Connect callback functions to VisPy Canvas
            self._vispy_widget.canvas.events.mouse_press.connect(mode.press)
            self._vispy_widget.canvas.events.mouse_release.connect(mode.release)
            self._vispy_widget.canvas.events.mouse_move.connect(mode.move)
            self.disable_camera_events()
            # self._vispy_widget.canvas.update()
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