__author__ = 'penny'

"""
This is for getting the selection part and highlight it
"""
from ..common.toolbar import VispyDataViewerToolbar

import numpy as np
from matplotlib import path

from glue.core import Data
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)
        self.pos_data = None

    # TODO: same as scatter plot now, move to common later
    def get_visible_data(self):
        visible = []
        # Loop over visible layer artists
        for layer_artist in self._vispy_data_viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        visual = layer_artist.visual  # we only have one visual for each canvas
        return visible, visual

    def on_mouse_press(self, event):
        self.selection_origin = event.pos
        if self.mode is 'point':
            # TODO: add dendrogram selection here
            pass

    def on_mouse_release(self, event):
        # Get the visible datasets
        visible_data, visual = self.get_visible_data()

        if event.button == 1 and self.mode is not None and self.mode is not 'point':
            data = self.get_map_data()
            selection_path = path.Path(self.line_pos, closed=True)
            mask = selection_path.contains_points(data)  # ndarray

            print('pos_data.shape', self.pos_data.shape)
            new_mask = np.reshape(mask, self.pos_data.shape) # TODO: apply to all data
            new_mask = np.transpose(new_mask)
            new_mask = np.ravel(new_mask)
            # print('new mask shape', new_mask)
            self.mark_selected(new_mask, visible_data)

            # Reset lasso
            self.line_pos = []  # TODO: Empty pos input is not allowed for line_visual
            self.line.set_data(np.array(self.line_pos))
            self.line.update()

            self.selection_origin = (0, 0)

            self._vispy_widget.canvas.update()

    def mark_selected(self, mask, visible_data):

        # We now make a subset state. For scatter plots we'll want to use an
        # ElementSubsetState, while for cubes, we'll need to change to a
        # MaskSubsetState.
        subset_state = ElementSubsetState(np.where(mask)[0])
        print('i want to know where mask', np.where(mask))

#('i want to know where mask', (array([ 6,  6,  6, ..., 52, 52, 52]), array([101, 102, 102, ...,  51,  51,  51]), array([ 0,  0,  1, ..., 57, 58, 59])))'''

# this is after removing two lines
# ('i want to know where mask', (array([  5467,   5468,   5469, ..., 573298, 573299, 573300]),))

        # We now check what the selection mode is, and update the selection as
        # needed (this is delegated to the correct subset mode).
        mode = EditSubsetMode()
        focus = visible_data[0] if len(visible_data) > 0 else None
        mode.update(self._data_collection, subset_state, focus_data=focus)

    def get_map_data(self):

        # Get the visible datasets
        visible_data, visual = self.get_visible_data()
        layer = visible_data[0]
        # what's the difference between layer.data[attribute] & layer[attribute]
        # layer_data = np.array(layer.data[layer.attribute]).transpose()
        # print('layer_data, shape', layer_data, layer_data.shape)

        # TODO: multiple data here not work well now
        # A possible solution for multiple data would be combine them into a whole data set, like the np.append here
        # if len(visible_data) > 1:
        #     n = len(visible_data)
        #     for id in range(1, n):
        #         layer = visible_data[id]
        #         np.append(layer_data, np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose(), axis=0)

        tr = visual.node_transform(self._vispy_widget.view)
        pos_data = np.argwhere(np.transpose(np.ones(layer.data.shape)))
        data = tr.map(pos_data)[:, :2]
        self.pos_data = np.transpose(np.ones(layer.data.shape))
        return data