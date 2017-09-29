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

from ..common.selection_tools import VispyMouseMode, get_mask_for_layer_artist
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

            def selection(x, y):
                return (np.abs(x - event.pos[0]) < 2) & (np.abs(y - event.pos[1]) < 2)

            mask = get_mask_for_layer_artist(self.active_layer_artist, self.viewer, selection)

            self.mark_selected(mask, self.active_layer_artist.layer)

    def move(self, event):
        # add the knn scheme to decide selected region when moving mouse

        if SKLEARN_INSTALLED:
            if event.button == 1 and event.is_dragging:

                # TODO: support multiple datasets here

                # calculate the threshold and call draw visual
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                drag_distance = math.sqrt(width**2 + height**2)
                canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2 +
                                        self._vispy_widget.canvas.size[1]**2)

                # neighbor num proportioned to mouse moving distance
                n_neighbors = int(drag_distance / canvas_diag * self.active_layer_artist.layer.shape[0])
                if n_neighbors >= 1:

                    # TODO: this has to be applied in one go, not in chunks
                    def selection(x, y):
                        mask = np.zeros(x.shape, dtype=bool)
                        neigh = NearestNeighbors(n_neighbors=n_neighbors)
                        neigh.fit(np.vstack([x, y]).transpose())
                        select_index = neigh.kneighbors([self.selection_origin])[1]
                        mask[select_index] = 1
                        return mask

                    mask = get_mask_for_layer_artist(self.active_layer_artist, self.viewer, selection)

                    self.mark_selected(mask, self.active_layer_artist.layer)
