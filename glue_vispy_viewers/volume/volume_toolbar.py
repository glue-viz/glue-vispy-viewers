"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""
from ..common.toolbar import VispyDataViewerToolbar

import math
import numpy as np
from glue.core.roi import RectangularROI, CircularROI
from glue.utils.geometry import points_inside_poly
from ..utils import as_matrix_transform
from ..extern.vispy import scene

from .floodfill_scipy import floodfill_scipy


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget,
                                                     parent=parent)
        self.markers = scene.visuals.Markers(parent=self._vispy_widget.view.scene)

        self.visual_tr = None
        self.visible_data = None
        self.visual = None
        self.current_visible_array = None
        self.max_value_pos = None
        self.max_value = None


# todo: add global variable of self.visual, vol_data, vol_shape

    def on_mouse_press(self, event):
        """
        Assign mouse position and do point selection.
        :param event:
        """
        if self.mode:
            self.selection_origin = event.pos

            # Get all data sets visible in current viewer
            self.visible_data, self.visual = self.get_visible_data()
            self.current_visible_array = np.nan_to_num(self.visible_data[0]['PRIMARY'])
            self.visual_tr = self._vispy_widget.limit_transforms[self.visual]

        if self.mode is 'point':

            # get start and end point of ray line
            pos = self.get_ray_line()
            max_value_pos, max_value = self.get_inter_value(pos)
            self.max_value_pos = max_value_pos
            self.max_value = max_value

            # set marker and status text
            if max_value:
                self.markers.set_data(pos=np.array(max_value_pos),
                                      face_color='yellow')

            self._vispy_widget.canvas.update()

    def on_mouse_release(self, event):
        """
        Get the mask of selected data and get them highlighted.
        :param event:
        """
        # Get the visible datasets
        if event.button == 1 and self.mode and self.mode is not 'point':
            # visible_data, visual = self.get_visible_data()
            data = self.get_map_data()
            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            elif self.mode is 'lasso':
                # Note, we use points_inside_poly here instead of calling e.g.
                # matplotlib directly, because we include some optimizations
                # in points_inside_poly
                vx, vy = np.array(self.line_pos).transpose()
                x, y = data.transpose()
                mask = points_inside_poly(x, y, vx, vy)

            elif self.mode is 'ellipse':
                xmin, ymin = np.min(self.line_pos[:, 0]), \
                             np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), \
                             np.max(self.line_pos[:, 1])

                # (xc, yc, radius)
                c = CircularROI((xmax+xmin)/2., (ymax+ymin)/2., (xmax-xmin)/2.)
                mask = c.contains(data[:, 0], data[:, 1])

            elif self.mode is 'rectangle':
                xmin, ymin = np.min(self.line_pos[:, 0]), \
                             np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), \
                             np.max(self.line_pos[:, 1])
                r = RectangularROI(xmin, xmax, ymin, ymax)
                mask = r.contains(data[:, 0], data[:, 1])

            else:
                raise ValueError("Unknown mode: {0}".format(self.mode))

            # Shape selection mask is generated from mapped data, so it has the same shape as transposed data array.
            # The ravel here is to make mask compatible with ElementSubsetState input.
            shape_mask = np.reshape(mask, np.transpose(self.current_visible_array).shape)
            shape_mask = np.ravel(np.transpose(shape_mask))
            self.mark_selected(shape_mask, self.visible_data)

            self.lasso_reset()

    def on_mouse_move(self, event):

        super(VolumeSelectionToolbar, self).on_mouse_move(event=event)

        if event.button == 1 and event.is_dragging and self.mode is not None:
            if self.mode is 'point':

                # calculate the threshold and call draw visual
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                drag_distance = math.sqrt(width**2+height**2)
                canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2
                                        + self._vispy_widget.canvas.size[1]**2)

                mask = self.draw_floodfill_visual(drag_distance / canvas_diag)

                if mask is not None:
                    # Smart selection mask has the same shape as data shape.
                    smart_mask = np.reshape(mask, self.current_visible_array.shape)
                    smart_mask = np.ravel(smart_mask)
                    self.mark_selected(smart_mask, self.visible_data)

    def draw_floodfill_visual(self, threshold):
        formate_data = np.asarray(self.current_visible_array, np.float64)

        # Normalize the threshold so that it returns values in the range 1.01
        # to 101 (since it can currently be between 0 and 1)

        threshold = 1 + 10 ** (threshold * 4 - 2)

        trans = self.visual_tr.translate
        scale = self.visual_tr.scale

        max_value_pos = self.max_value_pos[0]

        # xyz index in volume array
        x = (max_value_pos[0] - trans[0])/scale[0]
        y = (max_value_pos[1] - trans[1])/scale[1]
        z = (max_value_pos[2] - trans[2])/scale[2]

        if self.max_value_pos:
            select_mask = floodfill_scipy(formate_data, (z, y, x), threshold)

            status_text = 'x=%.2f, y=%.2f, z=%.2f' % (x, y, z) \
                  + ' value=%.2f' % self.max_value
            self._vispy_data_viewer.show_status(status_text)

            return select_mask
        else:
            return None

    def get_map_data(self):
        """
        Get the mapped buffer from self.visual to canvas.

        :return: Mapped data position on canvas.
        """

        # Get the visible datasets
        data_object = self.visible_data[0]

        # TODO: add support for multiple data here, data_array should
        # cover all self.visible_data array

        tr = as_matrix_transform(self.visual.get_transform(map_from='visual',
                                                           map_to='canvas'))

        pos_data = np.indices(data_object.data.shape[::-1], dtype=float)
        pos_data = pos_data.reshape(3, -1).transpose()

        data = tr.map(pos_data)
        data /= data[:, 3:]   # normalize with homogeneous coordinates
        return data[:, :2]

    def get_inter_value(self, pos):
        trans = self.visual_tr.translate
        scale = self.visual_tr.scale

        inter_pos = []
        for z in range(0, self.current_visible_array.shape[0]):
            #   3D line defined with two points (x0, y0, z0) and (x1, y1, z1) as
            #   (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1) = (z - z1)/(z2 - z1) = t
            z = z * scale[2] + trans[2]
            t = (z - pos[0][2])/(pos[1][2] - pos[0][2])
            x = t * (pos[1][0] - pos[0][0]) + pos[0][0]
            y = t * (pos[1][1] - pos[0][1]) + pos[0][1]
            inter_pos.append([x, y, z])
        inter_pos = np.array(inter_pos)

        # cut the line within the cube
        m1 = inter_pos[:, 0] > trans[0]  # for x
        m2 = inter_pos[:, 0] < (self.current_visible_array.shape[2] * scale[0] + trans[0])
        m3 = inter_pos[:, 1] > trans[1]  # for y
        m4 = inter_pos[:, 1] < (self.current_visible_array.shape[1]*scale[1] + trans[1])
        inter_pos = inter_pos[m1 & m2 & m3 & m4]

        # set colors for markers
        colors = np.ones((inter_pos.shape[0], 4))
        colors[:] = (0.5, 0.5, 0, 1)

        # value of intersected points
        inter_value = []
        for each_point in inter_pos:
            x = (each_point[0] - trans[0])/scale[0]
            y = (each_point[1] - trans[1])/scale[1]
            z = (each_point[2] - trans[2])/scale[2]
            inter_value.append(self.current_visible_array[(z, y, x)])
        inter_value = np.array(inter_value)

        assert inter_value.shape[0] == inter_pos.shape[0]

        # TODO: there is a risk that no intersected points found here
        if len(inter_pos) == 0 or len(inter_value) == 0:
            print('empty selection list', inter_pos, inter_value)
            return None, None
        else:
            return [inter_pos[np.argmax(inter_value)]], inter_value.max()

    def get_ray_line(self):
        """
        Get the ray line from camera pos to the far point.

        :return: Start point and end point position.
        """
        tr_back = self.visual.get_transform(map_from='canvas', map_to='visual')

        _cam = self._vispy_widget.view.camera
        start_point = _cam.transform.map(_cam.center)

        end_point = np.insert(self.selection_origin, 2, 1)
        end_point = tr_back.map(end_point)

        # add the self.visual local transform
        end_point = self.visual_tr.map(end_point)
        end_point = end_point[:3] / end_point[3]

        return np.array([end_point, start_point[:3]])
