"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""
from ..common.toolbar import VispyDataViewerToolbar

import numpy as np
<<<<<<< HEAD
from glue.core.roi import RectangularROI, CircularROI
from glue.utils.geometry import points_inside_poly
from ..utils import as_matrix_transform
=======
from matplotlib import path

from glue.core.roi import RectangularROI, CircularROI
from ..extern.vispy import scene
>>>>>>> bdc6658... add ray line with transform not work correctly


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget, parent=parent)
        self.trans_ones_data = None
        # add some markers
        self.markers = scene.visuals.Markers(parent=self._vispy_widget.view.scene)
        self.trans = None
        self.scale = None
        self.visual_transform = None

# todo: add global variable of visual, vol_data, vol_shape

    def on_mouse_press(self, event):
        """
        Assign mouse position and do point selection.
        :param event:
        """
        self.selection_origin = event.pos
        print('event.pos', self.selection_origin)
        if self.mode is 'point':

            visible_data, visual = self.get_visible_data()
            data_object = visible_data[0]
            data_array = data_object['PRIMARY']

            self.trans = self._vispy_widget.limit_transforms[visual].translate
            self.scale = self._vispy_widget.limit_transforms[visual].scale
            self.visual_transform = self._vispy_widget.limit_transforms[visual]
            print('visual transform', self.visual_transform)

            pos = self.get_ray_line()

            # find the intersected points position in visual coordinate through z axis
            inter_pos = []

            for z in range(0, data_array.shape[0]):
                #   3D line defined with two points (x0, y0, z0) and (x1, y1, z1) as
                #   (x - x1)/(x2 - x1) = (y - y1)/(y2 - y1) = (z - z1)/(z2 - z1) = t
                z = z * self.scale[2] + self.trans[2]
                t = (z - pos[0][2])/(pos[1][2] - pos[0][2])
                x = t * (pos[1][0] - pos[0][0]) + pos[0][0]
                y = t * (pos[1][1] - pos[0][1]) + pos[0][1]
                inter_pos.append([x, y, z])
            inter_pos = np.array(inter_pos)
            # not correct here

            # cut the line within the cube
            m1 = inter_pos[:, 0] > self.trans[0] # or =?  for x
            m2 = inter_pos[:, 0] < (data_array.shape[2] * self.scale[0] + self.trans[0])
            m3 = inter_pos[:, 1] > self.trans[1]  # for y
            m4 = inter_pos[:, 1] < (data_array.shape[1]*self.scale[1] + self.trans[1])
            inter_pos = inter_pos[m1 & m2 & m3 & m4]

            # set colors for markers
            colors = np.ones((inter_pos.shape[0], 4))
            colors[:] = (0.5, 0.5, 0, 1)

            # value of intersected points
            inter_value = []
            for each_point in inter_pos:
                x = (each_point[0] - self.trans[0])/self.scale[0]
                y = (each_point[1] - self.trans[1])/self.scale[1]
                z = (each_point[2] - self.trans[2])/self.scale[2]
                inter_value.append(data_array[(z, y, x)])
            inter_value = np.array(inter_value)
            print('inter value, pos', inter_value.shape, inter_pos.shape)
            assert inter_value.shape[0] == inter_pos.shape[0]
            if len(inter_value) != 0:
                colors[np.argmax(inter_value)] = (1, 1, 0.5, 1)  # change the color of max value marker

            self.markers.set_data(pos=inter_pos, face_color=colors)
            # print('interpos is', inter_points_index, data_array)
            # update limit to make transform sync with the stretch  :)
            # self._vispy_widget.add_data_visual(self.markers)
            # self._vispy_widget._update_limits()
            self._vispy_widget.canvas.update()

    def on_mouse_release(self, event):
        """
        Get the mask of selected data and get them highlighted.
        :param event:
        """

        # Get the visible datasets
<<<<<<< HEAD
        if event.button == 1 and self.mode is not None:

=======
        if event.button == 1 and self.mode and self.mode is not 'point':
>>>>>>> bdc6658... add ray line with transform not work correctly
            visible_data, visual = self.get_visible_data()
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
                xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
                c = CircularROI((xmax + xmin) / 2., (ymax + ymin) / 2., (xmax - xmin) / 2.)  # (xc, yc, radius)
                mask = c.contains(data[:, 0], data[:, 1])

            elif self.mode is 'rectangle':
                xmin, ymin = np.min(self.line_pos[:, 0]), np.min(self.line_pos[:, 1])
                xmax, ymax = np.max(self.line_pos[:, 0]), np.max(self.line_pos[:, 1])
                r = RectangularROI(xmin, xmax, ymin, ymax)
                mask = r.contains(data[:, 0], data[:, 1])

            else:
                raise ValueError("Unknown mode: {0}".format(self.mode))

            # Mask matches transposed volume data set rather than the original one.
            # The ravel here is to make mask compatible with ElementSubsetState input.
            new_mask = np.reshape(mask, self.trans_ones_data.shape)
            new_mask = np.ravel(np.transpose(new_mask))
            self.mark_selected(new_mask, visible_data)

            self.lasso_reset()

    def get_map_data(self):
        """
        Get the mapped buffer from visual to canvas.

        :return: Mapped data position on canvas.
        """

        # Get the visible datasets
        visible_data, visual = self.get_visible_data()
        data_object = visible_data[0]

        # TODO: add support for multiple data here, data_array should cover all visible_data array

        tr = as_matrix_transform(visual.get_transform(map_from='visual', map_to='canvas'))

        self.trans_ones_data = np.transpose(np.ones(data_object.data.shape))

        pos_data = np.indices(layer.data.shape[::-1], dtype=float).reshape(3, -1).transpose()
        data = tr.map(pos_data)
        data /= data[:, 3:]   # normalize with homogeneous coordinates
        return data[:, :2]

    def get_ray_line(self):
        """
        Get the ray line from camera pos to the far point.

        :return: Start point and end point position.
        """
        visible_data, visual = self.get_visible_data()
        tr_back = visual.get_transform(map_from='canvas', map_to='visual') # TODO: put visual to self.visual
        print('=======================')
        print('chain transform', tr_back)
        print('=======================')

        # try add the visual's transform
        # tr_back = tr_back * self.visual_transform
        print('chain transform after visual', tr_back)
        print('=======================')

        _cam = self._vispy_widget.view.camera
        _cam_point = _cam.transform.map(_cam.center)  #TODO: this is not correct

        trpos_start = np.insert(self.selection_origin, 2, 1)
        trpos_start = tr_back.map(trpos_start)
        trpos_start = self.visual_transform.map(trpos_start)
        print('trpos_start after visual transform', trpos_start)

        trpos_start = trpos_start[:3] / trpos_start[3]

        return np.array([trpos_start, _cam_point[:3]])
