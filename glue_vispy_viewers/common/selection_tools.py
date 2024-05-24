"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""

import numpy as np

from glue.core import Data
from glue.config import viewer_tool

from glue.viewers.common.tool import CheckableTool

from glue.core.command import ApplySubsetState

from glue.core.roi import RectangularROI, CircularROI, PolygonalROI, Projected3dROI
from glue.core.subset import RoiSubsetState3d

from ..utils import as_matrix_transform
from vispy.scene import Rectangle, Line, Ellipse

# Backward-compatibility for reading files
from .compat import MultiMaskSubsetState  # noqa
MultiElementSubsetState = MultiMaskSubsetState


class VispyMouseMode(CheckableTool):

    # this will create an abstract selection mode class to handle mouse events
    # instanced by lasso, rectangle, circular and point mode

    def __init__(self, viewer):
        super(VispyMouseMode, self).__init__(viewer)
        self.current_visible_array = None

    def activate(self):
        if self.viewer is not None:
            self.viewer.toolbar._enable_tool_interactions(self)
        self.reset()

    def deactivate(self):
        if self.viewer is not None:
            self.viewer.toolbar._disable_tool_interactions(self)
        self.reset()

    def reset(self):
        pass

    @property
    def _vispy_widget(self):
        return self.viewer._vispy_widget

    def get_visible_data(self):
        visible = []
        # Loop over visible layer artists
        for layer_artist in self.viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        visual = layer_artist.visual  # we only have one visual for each canvas
        return visible, visual

    def iter_data_layer_artists(self):
        for layer_artist in self.viewer._layer_artist_container:
            if isinstance(layer_artist.layer, Data):
                yield layer_artist

    def apply_roi(self, roi):
        x_att = self.viewer.state.x_att
        y_att = self.viewer.state.y_att
        z_att = self.viewer.state.z_att
        self.apply_subset_state(RoiSubsetState3d(x_att, y_att, z_att, roi))

    def apply_subset_state(self, subset_state):
        cmd = ApplySubsetState(data_collection=self.viewer._data,
                               subset_state=subset_state)
        self.viewer.session.command_stack.do(cmd)

    def set_progress(self, value):
        if value < 0:
            self.viewer.show_status('')
        else:
            self.viewer.show_status('Calculating selection - {0}%'.format(int(value)))

    @property
    def projection_matrix(self):

        # Get first layer (maybe just get from viewer directly in future)
        layer_artist = next(self.iter_data_layer_artists())

        # Get transformation matrix and transpose
        transform = layer_artist.visual.get_transform(map_from='visual', map_to='canvas')
        return as_matrix_transform(transform).matrix.T


@viewer_tool
class LassoSelectionMode(VispyMouseMode):

    icon = 'glue_lasso'
    tool_id = 'vispy:lasso'
    action_text = 'Select data using a lasso selection'

    def __init__(self, viewer):
        super(LassoSelectionMode, self).__init__(viewer)
        self.line = Line(color='purple',
                         width=2, method='agg')

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

            if len(self.line_pos) > 0:
                vx, vy = np.array(self.line_pos).transpose()
                roi = Projected3dROI(roi_2d=PolygonalROI(vx, vy),
                                     projection_matrix=self.projection_matrix)
                self.apply_roi(roi)

            self.reset()

            self.viewer.toolbar.active_tool = None


@viewer_tool
class RectangleSelectionMode(VispyMouseMode):

    icon = 'glue_square'
    tool_id = 'vispy:rectangle'
    action_text = 'Select data using a rectangular selection'

    def __init__(self, viewer):
        super(RectangleSelectionMode, self).__init__(viewer)
        self.rectangle = Rectangle(center=(0, 0), width=1, height=1, border_width=2,
                                   color=(0, 0, 0, 0), border_color='purple')

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

            if self.corner2 is not None:
                roi = Projected3dROI(roi_2d=RectangularROI(*self.bounds),
                                     projection_matrix=self.projection_matrix)
                self.apply_roi(roi)

            self.reset()

            self.viewer.toolbar.active_tool = None


@viewer_tool
class CircleSelectionMode(VispyMouseMode):

    icon = 'glue_circle'
    tool_id = 'vispy:circle'
    action_text = 'Select data using a circular selection'

    def __init__(self, viewer):
        super(CircleSelectionMode, self).__init__(viewer)
        self.ellipse = Ellipse(center=(0, 0), radius=1, border_width=2,
                               color=(0, 0, 0, 0), border_color='purple')

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

        if event.button == 1:

            if self.radius > 0:
                roi = Projected3dROI(roi_2d=CircularROI(self.center[0],
                                                        self.center[1],
                                                        self.radius),
                                     projection_matrix=self.projection_matrix)
                self.apply_roi(roi)

            self.reset()

            self.viewer.toolbar.active_tool = None
