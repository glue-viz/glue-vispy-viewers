__author__ = 'penny'

"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""
from ..common.toolbar import VispyDataViewerToolbar

import numpy as np
from matplotlib import path


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)
        self.trans_ones_data = None

    def on_mouse_press(self, event):
        self.selection_origin = event.pos
        if self.mode is 'point':
            # TODO: add dendrogram selection here
            pass

    def on_mouse_release(self, event):

        visible_data, visual = self.get_visible_data()

        if event.button == 1 and self.mode is not None and self.mode is not 'point':
            data = self.get_map_data()
            selection_path = path.Path(self.line_pos, closed=True)
            mask = selection_path.contains_points(data)  # ndarray

            # Mask matches transposed volume data set rather than the original one.
            # The ravel here is to make mask compatible with ElementSubsetState input.
            new_mask = np.reshape(mask, self.trans_ones_data.shape)
            new_mask = np.ravel(np.transpose(new_mask))
            self.mark_selected(new_mask, visible_data)

            self.lasso_reset()

    def get_map_data(self):

        # Get the visible datasets
        visible_data, visual = self.get_visible_data()
        layer = visible_data[0]

        # TODO: add support for multiple data here, layer should cover all visible_data array

        tr = visual.node_transform(self._vispy_widget.view)
        self.trans_ones_data = np.transpose(np.ones(layer.data.shape))

        pos_data = np.argwhere(self.trans_ones_data)
        data = tr.map(pos_data)[:, :2]
        return data