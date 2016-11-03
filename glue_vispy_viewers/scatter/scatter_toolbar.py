"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""

import os
import math

import numpy as np
from matplotlib import path

try:
    from sklearn.neighbors import NearestNeighbors
    SKLEARN_INSTALLED = True
except ImportError:
    SKLEARN_INSTALLED = False

from glue.config import viewer_tool
from glue.core.roi import RectangularROI, CircularROI

from ..common.toolbar import VispyMouseMode
from ..utils import as_matrix_transform
from ..extern.vispy.scene import Rectangle, Line, Ellipse


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


@viewer_tool
class LassoSelectionMode(VispyMouseMode):

    icon = 'glue_lasso'
    tool_id = 'scatter3d:lasso'
    action_text = 'Select points using a lasso selection'

    def __init__(self, viewer):
        super(LassoSelectionMode, self).__init__(viewer)
        self.line = Line(color='purple',
                         width=2, method='agg',
                         parent=self._vispy_widget.canvas.scene)

    def activate(self):
        self.reset()

    def reset(self):
        self.line_pos = []
        self.line.set_data(np.zeros((0, 2), dtype=float))
        self.line.parent = None

    def press(self, event):
        if event.button == 1:
            self.line_pos.append(event.pos)

    def move(self, event):
        if event.button == 1 and event.is_dragging:
            self.line_pos.append(event.pos)
            self.line.set_data(np.array(self.line_pos, dtype=float))
            self.line.parent = self._vispy_widget.canvas.scene

    def release(self, event):
        if event.button == 1:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)
            if len(self.line_pos) > 0:
                selection_path = path.Path(self.line_pos, closed=True)
                mask = selection_path.contains_points(data)
                self.mark_selected(mask, visible_data)
            self.reset()


@viewer_tool
class RectangleSelectionMode(VispyMouseMode):

    icon = 'glue_square'
    tool_id = 'scatter3d:rectangle'
    action_text = 'Select points using a rectangular selection'

    def __init__(self, viewer):
        super(RectangleSelectionMode, self).__init__(viewer)
        self.rectangle = Rectangle(center=(0, 0), width=1, height=1, border_width=2,
                                   color=(0, 0, 0, 0), border_color='purple')

    def activate(self):
        self.reset()

    def reset(self):
        self.corner1 = None
        self.corner2 = None
        self.rectangle.parent = None

    def press(self, event):
        if event.button == 1:
            self.corner1 = event.pos

    def move(self, event):
        if event.button == 1 and event.is_dragging:
            self.corner2 = event.pos
            x1, y1 = self.corner1
            x2, y2 = self.corner2
            if abs(x2 - x1) > 0 and abs(y2 - y1) > 0:
                self.rectangle.center = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                self.rectangle.width = abs(x2 - x1)
                self.rectangle.height = abs(y2 - y1)
                self.rectangle.parent = self._vispy_widget.canvas.scene

    @property
    def bounds(self):
        x1, y1 = self.corner1
        x2, y2 = self.corner2
        return (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))

    def release(self, event):
        if event.button == 1:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)
            if self.corner2 is not None:
                r = RectangularROI(*self.bounds)
                mask = r.contains(data[:, 0], data[:, 1])
                self.mark_selected(mask, visible_data)
            self.reset()


@viewer_tool
class CircleSelectionMode(VispyMouseMode):

    icon = 'glue_circle'
    tool_id = 'scatter3d:circle'
    action_text = 'Select points using a circular selection'

    def __init__(self, viewer):
        super(CircleSelectionMode, self).__init__(viewer)
        self.ellipse = Ellipse(center=(0, 0), radius=1, border_width=2,
                               color=(0, 0, 0, 0), border_color='purple')

    def activate(self):
        self.reset()

    def reset(self):
        self.center = None
        self.radius = 0
        self.ellipse.parent = None

    def press(self, event):
        if event.button == 1:
            self.center = event.pos

    def move(self, event):
        if event.button == 1 and event.is_dragging:
            self.radius = max(abs(event.pos[0] - self.center[0]),
                              abs(event.pos[1] - self.center[1]))
            if self.radius > 0:
                self.ellipse.center = self.center
                self.ellipse.radius = self.radius
                self.ellipse.parent = self._vispy_widget.canvas.scene

    def release(self, event):
        if event.button == 1 and self.tool_id:
            visible_data, visual = self.get_visible_data()
            data = get_map_data(visible_data, visual, self._vispy_widget)
            if self.radius > 0:
                c = CircularROI(self.center[0], self.center[1], self.radius)
                mask = c.contains(data[:, 0], data[:, 1])
                self.mark_selected(mask, visible_data)
            self.reset()


# TODO: replace by knn selection mode

@viewer_tool
class PointSelectionMode(VispyMouseMode):

    icon = 'glue_point'
    tool_id = 'scatter3d:point'
    action_text = 'Select points using a point selection'

    def release(self, event):
        pass

    def press(self, event):

        if event.button == 1:

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
                drag_distance = math.sqrt(width**2 + height**2)
                canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2 +
                                        self._vispy_widget.canvas.size[1]**2)

                # neighbor num proportioned to mouse moving distance
                n_neighbors = drag_distance / canvas_diag * visible_data[0].data.shape[0]
                neigh = NearestNeighbors(n_neighbors=n_neighbors)
                neigh.fit(data)
                select_index = neigh.kneighbors([self.selection_origin])[1]

                mask = np.zeros(visible_data[0].data.shape)
                mask[select_index] = 1
                self.mark_selected(mask, visible_data)
