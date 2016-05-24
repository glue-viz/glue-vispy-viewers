"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""
from ..common.toolbar import VispyDataViewerToolbar
from glue.core.roi import RectangularROI, CircularROI
import numpy as np
from matplotlib import path


class ScatterSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(ScatterSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)

    # TODO: implement advanced point selection here
    def on_mouse_press(self, event):
        if self.mode is 'point':
            # Ray intersection on the CPU to highlight the selected point(s)
            data = self.get_map_data()

            # TODO: the threshold 2 here could replaced with a slider bar to control the selection region in the future
            m1 = data > (event.pos - 2)
            m2 = data < (event.pos + 2)

            array_mark = np.argwhere(m1[:, 0] & m1[:, 1] & m2[:, 0] & m2[:, 1])
            mask = np.zeros(len(data), dtype=bool)
            for i in array_mark:
                index = int(i[0])
                mask[index] = True
            visible_data, visual = self.get_visible_data()

            self.mark_selected(mask, visible_data)
            self._vispy_widget.canvas.update()

        else:
            self.selection_origin = event.pos

    def on_mouse_release(self, event):

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

            self.mark_selected(mask, visible_data)

            self.lasso_reset()

    def get_map_data(self):
        # Get the component IDs
        x_att = self._vispy_widget.options.x_att
        y_att = self._vispy_widget.options.y_att
        z_att = self._vispy_widget.options.z_att

        # Get the visible datasets
        visible_data, visual = self.get_visible_data()
        layer = visible_data[0]
        layer_data = np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose()

        # TODO: multiple data here not work well now
        # A possible solution for multiple data would be combine them into a whole data set, like the np.append here
        # if len(visible_data) > 1:
        #     n = len(visible_data)
        #     for id in range(1, n):
        #         layer = visible_data[id]
        #         np.append(layer_data, np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose(), axis=0)
        tr = visual.get_transform(map_from='visual', map_to='canvas')
        data = tr.map(layer_data)
        data /= data[:, 3:]  # normalize with homogeneous coordinates
        return data[:, :2]
