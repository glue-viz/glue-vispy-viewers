"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""

import math

import numpy as np

from glue.core import Subset
from glue.core.subset import FloodFillSubsetState
from glue.config import viewer_tool

from ..common.toolbar import VispyMouseMode
from vispy.scene import Markers
from .layer_artist import VolumeLayerArtist


@viewer_tool
class FloodFillSelectionMode(VispyMouseMode):

    icon = 'glue_point'
    tool_id = 'volume3d:floodfill'
    action_text = 'Select volume using a floodfill selection'

    def __init__(self, viewer):
        super(FloodFillSelectionMode, self).__init__(viewer)
        self.subset_state = None

    def release(self, event):
        pass

    def reset(self):
        if hasattr(self, 'markers'):
            self.markers.visible = False

    def press(self, event):
        """
        Assign mouse position and do point selection.
        :param event:
        """

        if not hasattr(self, 'markers'):
            self.markers = Markers(parent=self._vispy_widget.view.scene)

        if event.button == 1:

            self.selection_origin = event.pos

            self.visible_data, self.visual = self.get_visible_data()

            # Get the values of the currently active layer artist - we
            # specifically pick the layer artist that is selected in the layer
            # artist view in the left since we have to pick one.
            layer_artist = self.viewer._view.layer_list.current_artist()

            # If the layer artist is for a Subset not Data, pick the first Data
            # one instead (where the layer artist is a volume artist)
            if isinstance(layer_artist.layer, Subset):
                for layer_artist in self.iter_data_layer_artists():
                    if isinstance(layer_artist, VolumeLayerArtist):
                        break
                else:
                    return

            # TODO: figure out how to make the above choice more sensible. How
            #       does the user know which data layer will be used? Can we use
            #       all of them in this mode?

            self.current_visible_array = layer_artist.layer[layer_artist.state.attribute]
            self.active_layer_artist = layer_artist
            self.current_visible_layer = layer_artist.layer

            # Get start and end point of ray line
            pos = self.get_ray_line()

            # Find largest value along the ray
            start_pos, start_value = self.get_max_along_ray(pos)

            # set marker and status text
            if start_pos is None:

                self.markers.visible = False
                self.subset_state = None

            else:

                self.markers.set_data(pos=np.array([start_pos]),
                                      face_color='yellow')

                self.markers.visible = True
                self.subset_state = FloodFillSubsetState(self.current_visible_layer,
                                                         self.active_layer_artist.state.attribute,
                                                         self.position_to_array_index(start_pos),
                                                         start_value)

            self._vispy_widget.canvas.update()

    def position_to_array_index(self, pos):

        # Normalize the threshold so that it returns values in the range 1.01
        # to 101 (since it can currently be between 0 and 1)

        tr_visual = self._vispy_widget.limit_transforms[self.visual]

        trans = tr_visual.translate
        scale = tr_visual.scale

        # xyz index in volume array
        x = int(round((pos[0] - trans[0]) / scale[0]))
        y = int(round((pos[1] - trans[1]) / scale[1]))
        z = int(round((pos[2] - trans[2]) / scale[2]))

        return z, y, x

    def move(self, event):

        if event.button == 1 and event.is_dragging and self.subset_state is not None:

            # calculate the threshold and call draw visual
            width = event.pos[0] - self.selection_origin[0]
            height = event.pos[1] - self.selection_origin[1]
            drag_distance = math.sqrt(width**2 + height**2)
            canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2 +
                                    self._vispy_widget.canvas.size[1]**2)

            threshold = drag_distance / canvas_diag
            threshold = 1 + 10 ** (threshold * 4 - 2)

            self.subset_state.threshold = threshold

            self.apply_subset_state(self.subset_state)

    def get_max_along_ray(self, pos):

        tr_visual = self._vispy_widget.limit_transforms[self.visual]

        trans = tr_visual.translate
        scale = tr_visual.scale

        inter_pos = []
        for z in range(0, self.current_visible_array.shape[0]):
            #   3D line defined with two points (x0, y0, z0) and (x1, y1, z1) as
            #   (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1) = (z - z1)/(z2 - z1) = t
            z = z * scale[2] + trans[2]
            t = (z - pos[0][2]) / (pos[1][2] - pos[0][2])
            x = t * (pos[1][0] - pos[0][0]) + pos[0][0]
            y = t * (pos[1][1] - pos[0][1]) + pos[0][1]
            inter_pos.append([x, y, z])
        inter_pos = np.array(inter_pos)

        # cut the line within the cube
        m1 = inter_pos[:, 0] > trans[0]  # for x
        m2 = inter_pos[:, 0] < (self.current_visible_array.shape[2] * scale[0] + trans[0])
        m3 = inter_pos[:, 1] > trans[1]  # for y
        m4 = inter_pos[:, 1] < (self.current_visible_array.shape[1] * scale[1] + trans[1])
        inter_pos = inter_pos[m1 & m2 & m3 & m4]

        # set colors for markers
        colors = np.ones((inter_pos.shape[0], 4))
        colors[:] = (0.5, 0.5, 0, 1)

        # value of intersected points
        inter_value = []
        for each_point in inter_pos:
            x = int((each_point[0] - trans[0]) / scale[0])
            y = int((each_point[1] - trans[1]) / scale[1])
            z = int((each_point[2] - trans[2]) / scale[2])
            inter_value.append(self.current_visible_array[(z, y, x)])
        inter_value = np.nan_to_num(np.array(inter_value, dtype=float))

        assert inter_value.shape[0] == inter_pos.shape[0]

        # TODO: there is a risk that no intersected points found here
        if len(inter_pos) == 0 or len(inter_value) == 0:
            return None, None
        else:
            return inter_pos[np.argmax(inter_value)], inter_value.max()

    def get_ray_line(self):
        """
        Get the ray line from camera pos to the far point.

        :return: Start point and end point position.
        """

        tr_back = self.visual.get_transform(map_from='canvas', map_to='visual')
        tr_visual = self._vispy_widget.limit_transforms[self.visual]

        _cam = self._vispy_widget.view.camera
        start_point = _cam.transform.map(_cam.center)

        # If the camera is in the fov=0 mode, the start point is incorrect
        # and is still at the 'near' distance. We therefore move the camera
        # towards 'infinity' to get the right ray direction.
        if _cam.fov == 0:
            start_point[:3] *= 1e30

        end_point = np.append(self.selection_origin, 1e-5).astype(float)
        end_point = tr_back.map(end_point)

        # add the self.visual local transform
        end_point = tr_visual.map(end_point)
        end_point = end_point[:3] / end_point[3]

        return np.array([end_point, start_point[:3]])
