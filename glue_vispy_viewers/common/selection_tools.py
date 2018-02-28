from __future__ import absolute_import, division, print_function

"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""

import numpy as np

from glue.core import Data
from glue.config import viewer_tool
from glue.core.roi import RectangularROI, CircularROI
from glue.viewers.common.qt.tool import CheckableTool
from glue.core.subset import SubsetState, ElementSubsetState
from glue.core.exceptions import IncompatibleAttribute
from glue.core.edit_subset_mode import EditSubsetMode
from glue.utils.geometry import points_inside_poly

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

    def mark_selected(self, mask, data):
        # We now make a subset state. For scatter plots we'll want to use an
        # ElementSubsetState, while for cubes, we'll need to change to a
        # MaskSubsetState.
        subset_state = ElementSubsetState(indices=np.where(mask)[0], data=data)

        # We now check what the selection mode is, and update the selection as
        # needed (this is delegated to the correct subset mode).
        try:
            mode = self.viewer.session.edit_subset_mode
        except AttributeError:  # old versisons of glue
            mode = EditSubsetMode()
        mode.update(self.viewer._data, subset_state, focus_data=data)

    def mark_selected_dict(self, mask_dict):
        subset_state = MultiMaskSubsetState(mask_dict=mask_dict)
        if len(mask_dict) > 0:
            try:
                mode = self.viewer.session.edit_subset_mode
            except AttributeError:  # old versisons of glue
                mode = EditSubsetMode()
            mode.update(self.viewer._data, subset_state, focus_data=list(mask_dict)[0])

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


def get_mask_from_scatter(data, visual, vispy_widget, selection, progress=None):

    # Get the component IDs
    x_att = vispy_widget.viewer_state.x_att
    y_att = vispy_widget.viewer_state.y_att
    z_att = vispy_widget.viewer_state.z_att

    # Get the visible data
    layer_data = np.nan_to_num([data[x_att],
                                data[y_att],
                                data[z_att]]).transpose()

    tr = as_matrix_transform(visual.get_transform(map_from='visual', map_to='canvas'))
    data = tr.map(layer_data)
    data /= data[:, 3:]  # normalize with homogeneous coordinates

    return selection(data[:, 0], data[:, 1])


def get_mask_from_volume(data, visual, selection, progress=None):
    """
    Get the mapped buffer from self.visual to canvas.

    :return: Mapped data position on canvas.
    """

    # For large volumes, the code in this function would take up very large
    # amounts of memory, so we need to proceed in chunks. The chunk size is
    # chosen so that the chunking has negligeable performance implications.

    chunk_size = 1000000

    tr = as_matrix_transform(visual.get_transform(map_from='visual',
                                                  map_to='canvas'))

    # We chunk by selecting C-contiguous sets of data slices. We do this by
    # first finding the number of elements along each slice then finding the
    # numbe of slices we can fit in the chunk size

    values_per_slice = data.shape[1] * data.shape[2]
    slices_per_chunk = max(chunk_size // values_per_slice, 1)
    n_chunks = max(data.shape[0] // slices_per_chunk, 1)

    mask = np.zeros(data.shape, dtype=bool)

    for chunk in range(n_chunks):

        imin = chunk * slices_per_chunk
        imax = min((chunk + 1) * slices_per_chunk, data.shape[0])

        chunk_shape = (imax - imin,) + data.shape[1:]

        pos_data = np.indices(chunk_shape[::-1], dtype=float)
        pos_data[2] += imin
        pos_data = pos_data.reshape(3, -1).transpose()

        data_sub = tr.map(pos_data)

        data_sub /= data_sub[:, 3:]   # normalize with homogeneous coordinates

        mask_sub = selection(data_sub[:, 0], data_sub[:, 1])

        mask_sub = np.reshape(mask_sub, chunk_shape[::-1])
        mask_sub = np.transpose(mask_sub)

        mask[imin:imax] = mask_sub

        if progress is not None:
            progress(100. * (chunk + 1) / n_chunks)

    return mask


def get_mask_for_layer_artist(layer_artist, viewer, selection, progress=None):

    from ..scatter.layer_artist import ScatterLayerArtist
    from ..volume.layer_artist import VolumeLayerArtist

    if isinstance(layer_artist, ScatterLayerArtist):
        return get_mask_from_scatter(layer_artist.layer, layer_artist.visual,
                                     viewer._vispy_widget, selection, progress=progress)
    elif isinstance(layer_artist, VolumeLayerArtist):
        return get_mask_from_volume(layer_artist.layer, layer_artist.visual,
                                    selection, progress=progress)
    else:
        raise Exception("Unknown layer type: {0}".format(type(layer_artist)))


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

                mask_dict = {}

                self.set_progress(0)

                for layer_artist in self.iter_data_layer_artists():

                    vx, vy = np.array(self.line_pos).transpose()

                    def selection(x, y):
                        return points_inside_poly(x, y, vx, vy)

                    mask = get_mask_for_layer_artist(layer_artist, self.viewer,
                                                     selection, progress=self.set_progress)

                    mask_dict[layer_artist.layer] = mask

                self.mark_selected_dict(mask_dict)

                self.set_progress(-1)

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

                r = RectangularROI(*self.bounds)

                mask_dict = {}

                self.set_progress(0)

                for layer_artist in self.iter_data_layer_artists():

                    def selection(x, y):
                        return r.contains(x, y)

                    mask = get_mask_for_layer_artist(layer_artist, self.viewer,
                                                     selection, progress=self.set_progress)

                    mask_dict[layer_artist.layer] = mask

                self.mark_selected_dict(mask_dict)

                self.set_progress(-1)

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

                mask_dict = {}

                self.set_progress(0)

                for layer_artist in self.iter_data_layer_artists():

                    def selection(x, y):
                        return c.contains(x, y)

                    mask = get_mask_for_layer_artist(layer_artist, self.viewer,
                                                     selection, progress=self.set_progress)

                    mask_dict[layer_artist.layer] = mask

                self.mark_selected_dict(mask_dict)

                self.set_progress(-1)

            self.reset()
