"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""
from ..common.toolbar import VispyViewerToolbar, VispyMouseMode
from glue.core.roi import RectangularROI, CircularROI
from ..utils import as_matrix_transform
import numpy as np
from matplotlib import path
import math
try:
    from sklearn.neighbors import NearestNeighbors
    SKLEARN_INSTALLED = True
except ImportError:
    SKLEARN_INSTALLED = False

try:
    from glue.external.qt import QtCore, QtGui as QtWidgets, QtGui
    def getsavefilename(*args, **kwargs):
        if 'filters' in kwargs:
            kwargs['filter'] = kwargs.pop('filters')
        return QtWidgets.QFileDialog.getSaveFileName(*args, **kwargs)
except ImportError:
    from qtpy import QtCore, QtWidgets, QtGui
    from qtpy.compat import getsavefilename

from glue.icons.qt import get_icon
import os

POINT_ICON = os.path.join(os.path.dirname(__file__), 'glue_point.png')


def get_map_data(visible_data, visual, vispy_widget):
    # Get the component IDs
    x_att = vispy_widget.options.x_att
    y_att = vispy_widget.options.y_att
    z_att = vispy_widget.options.z_att

    # Get the visible datasets
    layer = visible_data[0]
    layer_data = np.nan_to_num([layer[x_att], layer[y_att], layer[z_att]]).transpose()

    # TODO: multiple data here not work well now
    # A possible solution for multiple data would be combine them into a whole data set, like the np.append here
    # if len(visible_data) > 1:
    #     n = len(visible_data)
    #     for id in range(1, n):
    #         layer = visible_data[id]
    #         np.append(layer_data, np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose(), axis=0)
    tr = as_matrix_transform(visual.get_transform(map_from='visual', map_to='canvas'))
    data = tr.map(layer_data)
    data /= data[:, 3:]  # normalize with homogeneous coordinates
    return data[:, :2]


# TODO: release function could be reduced for lasso, rec and circle
# the same for volume and isosurface
class LassoSelectionMode(VispyMouseMode):
    def __init__(self, viewer):
        super(LassoSelectionMode, self).__init__(viewer)
        self.icon = get_icon('glue_lasso')
        self.tool_id = 'Scat:Lasso'
        self._data_collection = viewer._data
        self._vispy_widget = viewer._vispy_widget

    def release(self, event):
        # Get the visible datasets
        if event.button == 1 and self.tool_id:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)

            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            selection_path = path.Path(self.line_pos, closed=True)
            mask = selection_path.contains_points(data)

            self.mark_selected(mask, visible_data)

            self.lasso_reset()


class RectangleSelectionMode(VispyMouseMode):
    def __init__(self, viewer):
        super(RectangleSelectionMode, self).__init__(viewer)
        self.icon = get_icon('glue_square')
        self.tool_id = 'Scat:Rectangle'
        self._data_collection = viewer._data
        self._vispy_widget = viewer._vispy_widget

    def release(self, event):
        # Get the visible datasets
        if event.button == 1 and self.tool_id:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)

            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
            xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
            r = RectangularROI(xmin, xmax, ymin, ymax)
            mask = r.contains(data[:, 0], data[:, 1])

            self.mark_selected(mask, visible_data)

            self.lasso_reset()


class CircleSelectionMode(VispyMouseMode):
    def __init__(self, viewer):
        super(CircleSelectionMode, self).__init__(viewer)
        self.icon = get_icon('glue_circle')
        self.tool_id = 'Scat:Circle'
        self._data_collection = viewer._data
        self._vispy_widget = viewer._vispy_widget

    def release(self, event):
        # Get the visible datasets
        if event.button == 1 and self.tool_id:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)

            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
            xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
            c = CircularROI((xmax + xmin) / 2., (ymax + ymin) / 2., (xmax - xmin) / 2.)  # (xc, yc, radius)
            mask = c.contains(data[:, 0], data[:, 1])

            self.mark_selected(mask, visible_data)

            self.lasso_reset()


# TODO: replaced by knn selection mode
class PointSelectionMode(VispyMouseMode):
    def __init__(self, viewer):
        super(PointSelectionMode, self).__init__(viewer)
        self.icon = QtGui.QIcon(POINT_ICON)
        self.tool_id = 'Scat:Point'
        self._data_collection = viewer._data
        self._vispy_widget = viewer._vispy_widget

    def press(self, event):
        self.selection_origin = event.pos
        visible_data, visual = self.get_visible_data()

        # Ray intersection on the CPU to highlight the selected point(s)
        data = get_map_data(visible_data, visual, self._vispy_widget)

        # TODO: the threshold 2 here could replaced with a slider bar to
        # control the selection region in the future
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

    def move(self, event):
        # add the knn scheme to decide selected region when moving mouse

        if SKLEARN_INSTALLED:
            if event.button == 1 and event.is_dragging:
                visible_data, visual = self.get_visible_data()
                data = get_map_data(visible_data, visual, self._vispy_widget)

                visible_data = np.nan_to_num(visible_data)

                # calculate the threshold and call draw visual
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                drag_distance = math.sqrt(width**2+height**2)
                canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2
                                        + self._vispy_widget.canvas.size[1]**2)

                # neighbor num proportioned to mouse moving distance
                n_neighbors = drag_distance / canvas_diag * visible_data[0].data.shape[0]
                neigh = NearestNeighbors(n_neighbors=n_neighbors)
                neigh.fit(data)
                select_index = neigh.kneighbors([self.selection_origin])[1]

                mask = np.zeros(visible_data[0].data.shape)
                mask[select_index] = 1
                self.mark_selected(mask, visible_data)


class ScatterSelectionToolbar(VispyViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(ScatterSelectionToolbar, self).__init__(vispy_widget=vispy_widget,
                                                      parent=parent)
        # add tools here
        lasso_mode = LassoSelectionMode(self.parent())
        self.add_tool(lasso_mode)

        rectangle_mode = RectangleSelectionMode(self.parent())
        self.add_tool(rectangle_mode)

        circle_mode = CircleSelectionMode(self.parent())
        self.add_tool(circle_mode)

        point_mode = PointSelectionMode(self.parent())
        self.add_tool(point_mode)