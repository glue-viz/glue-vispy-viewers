__author__ = 'penny'

"""
This is for getting the selection part and highlight it
"""
from ..common.toolbar import VispyDataViewerToolbar
import numpy as np
from matplotlib import path

from glue.core import Data


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)
        self.vol_data = None

    # TODO: get current visual and volume data
    def get_visible_data(self):
        pass

    def on_mouse_press(self, event):
        self.selection_origin = event.pos
        if self.mode is 'point':
            # TODO: add dendrogram selection here
            pass

    def on_mouse_move(self, event):
        pass

    def on_mouse_release(self, event):
        pass