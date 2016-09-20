"""
This file will replace current toolbar and tools
all button functions will be implemented as a tool function
"""


from __future__ import absolute_import, division, print_function

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

from glue.config import viewer_tool
from glue.viewers.common.qt.tool import Tool, CheckableTool

from glue.icons.qt import get_icon
from glue.utils import nonpartial

try:
    from glue.external.qt import QtCore, QtGui as QtWidgets, QtGui
    def getsavefilename(*args, **kwargs):
        if 'filters' in kwargs:
            kwargs['filter'] = kwargs.pop('filters')
        return QtWidgets.QFileDialog.getSaveFileName(*args, **kwargs)
except ImportError:
    from qtpy import QtCore, QtWidgets, QtGui
    from qtpy.compat import getsavefilename


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


class VispyViewerToolbar(BasicToolbar):

    def __init__(self, parent): #parent would be a viewer
        print('vispyviewer toolbar parent is', parent)
        self._vispy_widget = parent._vispy_widget
        self.canvas = parent._vispy_widget.canvas

        BasicToolbar.__init__(self, parent)

    def setup_default_modes(self):
        save_mode = SaveTool(self.parent())
        self.add_tool(save_mode)

        # more goes here

    def activate_tool(self, mode):
        # if mode is instance of selection mode
                # Connect callback functions to VisPy Canvas
        # self._vispy_widget.canvas.events.mouse_press.connect(self.on_mouse_press)
        # self._vispy_widget.canvas.events.mouse_release.connect(self.on_mouse_release)
        # self._vispy_widget.canvas.events.mouse_move.connect(self.on_mouse_move)
        # self.enable_camera_events()
        super(VispyViewerToolbar, self).activate_tool(mode)

    def deactivate_tool(self, mode):
        # self.disable_camera_events()
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