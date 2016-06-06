"""
This is for 3D selection in Glue 3d volume rendering viewer, with shape selection and advanced
selection (not available now).
"""
from ..common.toolbar import VispyDataViewerToolbar

import numpy as np
from matplotlib import path
from glue.core.roi import RectangularROI, CircularROI
from ..extern.vispy import scene


class VolumeSelectionToolbar(VispyDataViewerToolbar):

    def __init__(self, vispy_widget=None, parent=None):
        super(VolumeSelectionToolbar, self).__init__(vispy_widget=vispy_widget,
                                                     parent=parent)
        self.trans_ones_data = None
        # add some markers
        self.markers = scene.visuals.Markers(parent=self._vispy_widget.view.scene)
        self.ray_line = scene.visuals.Line(color='green', width=5,
                                           parent=self._vispy_widget.view.scene)

        self.visual_tr = None
        self.visible_data = None
        self.visual = None


# todo: add global variable of self.visual, vol_data, vol_shape

    def on_mouse_press(self, event):
        """
        Assign mouse position and do point selection.
        :param event:
        """
        if self.mode:
            # do the initiation here
            self.selection_origin = event.pos
            self.visible_data, self.visual = self.get_visible_data()
            data_array = self.visible_data[0]['PRIMARY']
            self.visual_tr = self._vispy_widget.limit_transforms[self.visual]

        if self.mode is 'point':
            trans = self.visual_tr.translate
            scale = self.visual_tr.scale

            # get start and end point of ray line
            pos = self.get_ray_line()

            inter_pos = []
            for z in range(0, data_array.shape[0]):
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
            m2 = inter_pos[:, 0] < (data_array.shape[2] * scale[0] + trans[0])
            m3 = inter_pos[:, 1] > trans[1]  # for y
            m4 = inter_pos[:, 1] < (data_array.shape[1]*scale[1] + trans[1])
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
                inter_value.append(data_array[(z, y, x)])
            inter_value = np.array(inter_value)

            assert inter_value.shape[0] == inter_pos.shape[0]

            # change the color of max value marker
            if len(inter_value) != 0:
                self.markers.set_data(pos=np.array([inter_pos[np.argmax(inter_value)]]),
                                      face_color='yellow')
                status_text = 'pos '+str(inter_pos[np.argmax(inter_value)]) \
                              + ' value '+str(inter_value.max())
                self._vispy_data_viewer.show_status(status_text)

            self._vispy_widget.canvas.update()

    def on_mouse_release(self, event):
        """
        Get the mask of selected data and get them highlighted.
        :param event:
        """
        # Get the visible data set
        if event.button == 1 and self.mode is not None:
            data = self.get_map_data()

            if len(self.line_pos) == 0:
                self.lasso_reset()
                return

            elif self.mode is 'lasso':
                selection_path = path.Path(self.line_pos, closed=True)
                mask = selection_path.contains_points(data)

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

            # Mask matches transposed volume data set rather than the original one.
            # The ravel here is to make mask compatible with ElementSubsetState input.
            new_mask = np.reshape(mask, self.trans_ones_data.shape)
            new_mask = np.ravel(np.transpose(new_mask))
            self.mark_selected(new_mask, self.visible_data)

            self.lasso_reset()

    def get_map_data(self):
        """
        Get the mapped buffer from self.visual to canvas.

        :return: Mapped data position on canvas.
        """

        # Get the visible datasets
        data_object = self.visible_data[0]

        # TODO: add support for multiple data here, data_array should
        # cover all self.visible_data array

        tr = self.visual.get_transform(map_from='visual', map_to='canvas')

        self.trans_ones_data = np.transpose(np.ones(data_object.data.shape))

        pos_data = np.argwhere(self.trans_ones_data)
        data = tr.map(pos_data)
        data /= data[:, 3:]   # normalize with homogeneous coordinates
        return data[:, :2]

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

        self.ray_line.set_data(np.array([end_point, start_point[:3]]))

        return np.array([end_point, start_point[:3]])
