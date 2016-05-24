"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""
from ..common.toolbar import VispyDataViewerToolbar

import numpy as np
from matplotlib import path
from glue.core.roi import RectangularROI, CircularROI


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

        # Get the visible datasets
        if event.button == 1 and self.mode is not None:
            visible_data, visual = self.get_visible_data()
            data = self.get_map_data()

            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            elif self.mode is 'lasso':
                selection_path = path.Path(self.line_pos, closed=True)
                mask = selection_path.contains_points(data)

            elif self.mode is 'ellipse':
                xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
                c = CircularROI((xmax + xmin) / 2., (ymax + ymin) / 2., (xmax - xmin) / 2.)  # (xc, yc, radius)
                mask = c.contains(data[:, 0], data[:, 1])

            elif self.mode is 'rectangle':
                xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
                r = RectangularROI(xmin, xmax, ymin, ymax)
                mask = r.contains(data[:, 0], data[:, 1])

            else:
                raise ValueError("Unknown mode: {0}".format(self.mode))

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

        tr = visual.get_transform(map_from='visual', map_to='canvas')

        self.trans_ones_data = np.transpose(np.ones(layer.data.shape))

        pos_data = np.argwhere(self.trans_ones_data)
        data = tr.map(pos_data)
        data /= data[:, 3:]   # normalize with homogeneous coordinates
        return data[:, :2]
