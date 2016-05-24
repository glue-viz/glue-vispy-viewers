__author__ = 'penny'

"""
This is for getting the selection part and highlight it
"""
from ..common.toolbar import VispyDataViewerToolbar


class IsosurfaceSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(IsosurfaceSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)
        self.vol_data = None

    # TODO: get current visual and volume data
    def get_visible_data(self):
        pass

    def on_mouse_press(self, event):
        pass

    def on_mouse_move(self, event):
        pass

    def on_mouse_release(self, event):
        pass
