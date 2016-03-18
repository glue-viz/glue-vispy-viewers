__author__ = 'penny'

"""
This is for getting the selection part and highlight it
"""
from ..common.toolbar import VispyDataViewerToolbar
from .layer_artist import ScatterLayerArtist
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState
import numpy as np
from matplotlib import path

from glue.core import Data

class ScatterSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(ScatterSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)

        self.scatter_data = None
        self.facecolor = np.ones((1064,4), dtype=np.float)
        self.white = (1.0, 1.0, 1.0, 1.0)
        self.black = (0.0, 0.0, 0.0, 0.0)

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        if value is not None:
            self._layer = value[0]
        else:
            self._layer = None

    def get_visible_data(self):
        visible = []
        # Loop over visible layer artists
        for layer_artist in self._vispy_data_viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        visual = layer_artist.visual  # we only have one visual for each canvas
        return visible, visual

    # TODO: implement advanced point selection here
    def on_mouse_press(self, event):
        self.selection_origin = event.pos
        if self.mode is 'point':
            # Ray intersection on the CPU to highlight the selected point(s)

            data = self.tr.map(self.data)[:, :2]
            print('data', data)
            m1 = data > (event.pos - 4)
            m2 = data < (event.pos + 4)

            self.selected = np.argwhere(m1[:,0] & m1[:,1] & m2[:,0] & m2[:,1])
            self.mark_selected()

    def on_mouse_release(self, event):

        # TODO: here we need to finalize the selection shape based on the mode

        # Get the component IDs
        x_att = self._vispy_widget.options.x_att
        y_att = self._vispy_widget.options.y_att
        z_att = self._vispy_widget.options.z_att

        # Get the visible datasets
        visible_data, visual = self.get_visible_data()

        layer = visible_data[0]
        layer_data = np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose()

        # TODO: test multiple data for this
        if len(visible_data) > 1:
            n = len(visible_data)
            for id in range(1, n):
                layer = visible_data[id]
                np.append(layer_data, np.array([layer[x_att], layer[y_att], layer[z_att]]).transpose(), axis=0)

        tr = visual.node_transform(self._vispy_widget.view)

        self._scatter = visual
        self.scatter_data = layer_data

        if event.button == 1 and self.mode is not None and self.mode is not 'point':
            data = tr.map(layer_data)[:, :2]
            selection_path = path.Path(self.line_pos, closed=True)
            mask = selection_path.contains_points(data)

            # We now make a subset state. For scatter plots we'll want to use an
            # ElementSubsetState, while for cubes, we'll need to change to a
            # MaskSubsetState.
            subset_state = ElementSubsetState(np.where(mask)[0])

            # We now check what the selection mode is, and update the selection as
            # needed (this is delegated to the correct subset mode).
            mode = EditSubsetMode()
            focus = visible_data[0] if len(visible_data) > 0 else None
            mode.update(self._data_collection, subset_state, focus_data=focus)

            # Reset lasso
            self.line_pos = []  # TODO: Empty pos input is not allowed for line_visual
            self.line.set_data(np.array(self.line_pos))
            self.line.update()

            self.selection_origin = (0, 0)

            self._vispy_widget.canvas.update()


