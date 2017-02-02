from __future__ import absolute_import, division, print_function

"""
This is for 3D selection in Glue 3d scatter plot viewer.
"""

import math

import numpy as np

try:
    from sklearn.neighbors import NearestNeighbors
    SKLEARN_INSTALLED = True
except ImportError:
    SKLEARN_INSTALLED = False

from glue.core import Subset
from glue.config import viewer_tool

from ..common.selection_tools import VispyMouseMode, get_map_data_scatter
from .layer_artist import ScatterLayerArtist

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

            # Get the values of the currently active layer artist - we
            # specifically pick the layer artist that is selected in the layer
            # artist view in the left since we have to pick one.
            layer_artist = self.viewer._view.layer_list.current_artist()

            # If the layer artist is for a Subset not Data, pick the first Data
            # one instead (where the layer artist is a scatter artist)
            if isinstance(layer_artist.layer, Subset):
                for layer_artist in self.iter_data_layer_artists():
                    if isinstance(layer_artist, ScatterLayerArtist):
                        break
                else:
                    return

            # TODO: figure out how to make the above choice more sensible. How
            #       does the user know which data layer will be used? Can we use
            #       all of them in this mode?

            self.active_layer_artist = layer_artist

            # Ray intersection on the CPU to highlight the selected point(s)
            data = get_map_data_scatter(self.active_layer_artist.layer,
                                        self.active_layer_artist.visual,
                                        self._vispy_widget)

            # TODO: the threshold 2 here could replaced with a slider bar to
            # control the selection region in the future
            m1 = data > (event.pos - 2)
            m2 = data < (event.pos + 2)

            array_mark = np.argwhere(m1[:, 0] & m1[:, 1] & m2[:, 0] & m2[:, 1])
            mask = np.zeros(len(data), dtype=bool)
            for i in array_mark:
                index = int(i[0])
                mask[index] = True

            self.mark_selected(mask, self.active_layer_artist.layer)

    def move(self, event):
        # add the knn scheme to decide selected region when moving mouse

        if SKLEARN_INSTALLED:
            if event.button == 1 and event.is_dragging:

                # TODO: support multiple datasets here
                data = get_map_data_scatter(self.active_layer_artist.layer,
                                            self.active_layer_artist.visual,
                                            self._vispy_widget)

                # calculate the threshold and call draw visual
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                drag_distance = math.sqrt(width**2 + height**2)
                canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2 +
                                        self._vispy_widget.canvas.size[1]**2)

                mask = np.zeros(self.active_layer_artist.layer.shape)

                # neighbor num proportioned to mouse moving distance
                n_neighbors = drag_distance / canvas_diag * self.active_layer_artist.layer.shape[0]
                if n_neighbors >= 1:
                    neigh = NearestNeighbors(n_neighbors=n_neighbors)
                    neigh.fit(data)
                    select_index = neigh.kneighbors([self.selection_origin])[1]
                    mask[select_index] = 1
                self.mark_selected(mask, self.active_layer_artist.layer)
