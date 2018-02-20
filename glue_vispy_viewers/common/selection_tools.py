from __future__ import absolute_import, division, print_function

"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""

import numpy as np

from glue.core import Data
from glue.config import viewer_tool
from glue.core.roi import RectangularROI, CircularROI
from glue.viewers.common.qt.tool import CheckableTool
from glue.core.subset import SubsetState
from glue.core.exceptions import IncompatibleAttribute
from glue.core.edit_subset_mode import EditSubsetMode

from glue.core.roi import PolygonalProjected3dROI
from glue.core.subset import RoiSubsetState3d

from ..utils import as_matrix_transform
from ..extern.vispy.scene import Rectangle, Line, Ellipse


class VispyMouseMode(CheckableTool):

    # this will create an abstract selection mode class to handle mouse events
    # instanced by lasso, rectangle, circular and point mode

    def __init__(self, viewer):
        super(VispyMouseMode, self).__init__(viewer)
        self._vispy_widget = viewer._vispy_widget
        self.current_visible_array = None

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
        subset_state = RoiSubsetState3d(x_att, y_att, z_att, roi)
        try:
            mode = self.viewer.session.edit_subset_mode
        except AttributeError:  # old versisons of glue
            mode = EditSubsetMode()
        mode.update(self.viewer._data, subset_state)

    def set_progress(self, value):
        if value < 0:
            self.viewer.show_status('')
        else:
            self.viewer.show_status('Calculating selection - {0}%'.format(int(value)))


class MultiMaskSubsetState(SubsetState):
    """
    A subset state that can include a different mask for different datasets.

    This is useful when doing 3D selections with multiple datasets. This used
    to be a class called MultiElementSubsetState but it is more efficient to
    store masks than element lists. However, for backward-compatibility,
    values of the mask_dict dictionary can be index lists (recognzied because
    they don't have a boolean type).
    """

    def __init__(self, mask_dict=None):
        super(MultiMaskSubsetState, self).__init__()
        mask_dict_uuid = {}
        for key in mask_dict:
            if isinstance(key, Data):
                mask_dict_uuid[key.uuid] = mask_dict[key]
            else:
                mask_dict_uuid[key] = mask_dict[key]
        self._mask_dict = mask_dict_uuid

    def to_mask(self, data, view=None):
        if data.uuid in self._mask_dict:
            mask = self._mask_dict[data.uuid]
            if mask.dtype.kind != 'b':  # backward-compatibility with indices_dict
                indices = mask
                mask = np.zeros(data.shape, dtype=bool)
                mask.flat[indices] = True
            if view is not None:
                mask = mask[view]
            return mask
        else:
            raise IncompatibleAttribute()

    def copy(self):
        state = MultiMaskSubsetState(mask_dict=self._mask_dict)
        return state

    def __gluestate__(self, context):
        serialized = {key: context.do(value) for key, value in self._mask_dict.items()}
        return {'mask_dict': serialized}

    @classmethod
    def __setgluestate__(cls, rec, context):
        # For backward-compatibility reasons we recognize indices_dict
        if 'indices_dict' in rec:
            mask_dict = {key: context.object(value) for key, value in rec['indices_dict'].items()}
        else:
            mask_dict = {key: context.object(value) for key, value in rec['mask_dict'].items()}
        state = cls(mask_dict=mask_dict)
        return state


# Backward-compatibility for reading files
MultiElementSubsetState = MultiMaskSubsetState


@viewer_tool
class LassoSelectionMode(VispyMouseMode):

    icon = 'glue_lasso'
    tool_id = 'vispy:lasso'
    action_text = 'Select data using a lasso selection'

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

            if len(self.line_pos) > 0:

                # Get polygon
                vx, vy = np.array(self.line_pos).transpose()

                # Get first layer (maybe just get from viewer directly in future)
                layer_artist = next(self.iter_data_layer_artists())

                # Get transformation matrix and transpose
                transform = layer_artist.visual.get_transform(map_from='visual', map_to='canvas')
                projection_matrix = as_matrix_transform(transform).matrix.T

                # Create ROI
                roi = PolygonalProjected3dROI(vx, vy, projection_matrix)

                # Apply ROI to do selection
                self.apply_roi(roi)

            self.reset()


@viewer_tool
class RectangleSelectionMode(VispyMouseMode):

    icon = 'glue_square'
    tool_id = 'vispy:rectangle'
    action_text = 'Select data using a rectangular selection'

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

            if self.corner2 is not None:

                # To implement
                r = RectangularROI(*self.bounds)
                raise NotImplementedError()

            self.reset()


@viewer_tool
class CircleSelectionMode(VispyMouseMode):

    icon = 'glue_circle'
    tool_id = 'vispy:circle'
    action_text = 'Select data using a circular selection'

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

        if event.button == 1:

            if self.radius > 0:
                c = CircularROI(self.center[0], self.center[1], self.radius)
                raise NotImplementedError()

            self.reset()
