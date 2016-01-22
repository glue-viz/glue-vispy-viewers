from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app
from vispy.color import get_colormap, Color
from math import cos, sin, asin, radians, degrees, tan

from vispy.visuals import transforms


__all__ = ['QtScatVispyWidget']

# TODO : create a custom visual inherited from Markers
class QtScatVispyWidget(QtGui.QWidget):
    def __init__(self, parent=None):

        super(QtScatVispyWidget, self).__init__(parent=parent)

        # Prepare canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=False, always_on_top=False)
        self.canvas.measure_fps()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.canvas.central_widget.add_view()
        self.view.border_color = 'red'
        self.view.parent = self.canvas.scene
        self.turn_cam = scene.cameras.TurntableCamera(parent=self.view.scene, name='Turntable')
        self.view.camera = self.turn_cam # or try 'arcball'

        self.data = None
        self.axes_names = None
        self._current_array = None

        # create scatter object and fill in the data
        self.scat_visual = None

        """
        Use scat_data and scat_data_refresh to make the scatter visual consistent with
        stretch scale and threshold/clim
        Because the realization of stretch scale and threshold/clim is through update & modify the visual data
        """
        self.scat_data = None
        self.scat_data_refresh = None

        # Add a grid plane
        self.grid = scene.visuals.GridLines(scale=(0.5, 0.5), parent=self.view)

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        # Set a flag to make the transform just work once
        self.trans_flag = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if data is None:
            self._data = data
        else:
            self._data = data
            self.options_widget.set_valid_components([c.label for c in data.component_ids()])
            self._refresh()

    @property
    def components(self):
        if self.data is None:
            return None
        else:
            components = [self.data[self.options_widget.ui.xAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.yAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.zAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.SizeComboBox.currentText()],
                          self.data[self.options_widget.ui.ClimComboBox.currentText()]]
            return components

    def set_subsets(self, subsets):
        self.subsets = subsets

    def add_scatter_visual(self):
        if self.data is None:
            return None
        else:
            if not hasattr(self, 'components'): return
            n = len(self.components[3])
            P = np.zeros((n, 3), dtype=np.float32)

            X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
            X[...] = self.components[0]
            Y[...] = self.components[1]
            Z[...] = self.components[2]

            S = np.zeros(n)
            # Normalize the size based on median value of selected property to between 1-10
            m = np.median(np.nan_to_num(self.components[3]))

            if m < 1.0 or m > 10.0:
                S[...] = self.components[3] * (1.0/m)
            else:
                S[...] = self.components[3]

            scatter_color = Color(self.options_widget.true_color, self.options_widget.opacity/100.0)
            scat_visual = scene.visuals.Markers()
            scat_visual.set_data(P, symbol='disc', edge_color=None, face_color=scatter_color, size=S)
            self.scat_visual = scat_visual
            # Save this for refresh
            self.scat_data = [P, scatter_color, S]
            self.view.add(self.scat_visual)

            if self.trans_flag == 0:
                # Set transform for axis and camera
                self.set_transform([self.components[0], self.components[1], self.components[2]], self.components[3])

            self.update_clim()
            self.canvas.update()

    # TODO: I should put all update of visual data into this update_scatter_visual function
    # and all updates of those UI options into _refresh and use it to call the update_scatter_visual to
    # update current visual !

    def update_scatter_visual(self):
        """
        This method is called when basic properties for scatter visual got updated
        including the selection of axis & size combobox
        """
        P = self.scat_data[0]
        scatter_color = self.scat_data[1]
        S = self.scat_data[2]
        self.scat_visual.set_data(P, symbol='disc', edge_color=None, face_color=scatter_color, size=S)
        self.set_transform([self.components[0], self.components[1], self.components[2]], self.components[3])
        self.update_clim()
        self.canvas.update()

    def _refresh(self):
        """
        This method can be called if the stretch & opacity sliders are updated.
        """
        if self.data is None:
            return

        if self.scat_visual is not None and self.scat_data is not None:
            stretch_scale = self.options_widget.stretch
            # stretch_tran = [-0.5 * stretch_scale[idx] * len(self.components[2-idx]) for idx in range(3)]
            P = self.scat_data[0]
            n = P.shape[0]
            new_P = np.zeros((n, 3), dtype=np.float32)
            for idx in range(3):
                new_P[:, idx] = P[:, idx] * stretch_scale[idx]

            S = self.scat_data[2]
            new_S = np.zeros(n)
            new_S = S[...] * stretch_scale[3]

            scatter_color = Color(self.options_widget.true_color, self.options_widget.opacity/100.0)

            self.scat_visual.set_data(new_P, symbol='disc', edge_color=None,
                                      face_color=scatter_color, size=new_S)

            # Update the transform according to the stretch made here
            self.set_transform([new_P[:, 0], new_P[:, 1], new_P[:, 2]], new_S)
            self.scat_data_refresh = [new_P, scatter_color, new_S]

    def apply_clim(self):
        """
        This method can be called if the clim max & min textbox got updated
        """
        # TODO: put it together with _refresh
        currentid = self.options_widget.ui.ClimComboBox.currentText()
        _clim_pro = self.data[currentid]

        # self.options_widget.cmin is in unicode type
        _cmin = float(self.options_widget.cmin)
        _cmax = float(self.options_widget.cmax)

        # Get new clim_components according to the filter
        more = _clim_pro > _cmin
        less = _clim_pro < _cmax
        clim_filter = np.all([more, less], axis=0)
        _clim_scat_data = self.clim_for_scat_data(clim_filter)  # [position, color, size]

        n = len(_clim_scat_data[0])
        P = np.zeros((n, 3), dtype=np.float32)

        X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
        X[...] = _clim_scat_data[0]
        Y[...] = _clim_scat_data[1]
        Z[...] = _clim_scat_data[2]

        # Dot size determination according to the mass - *2 for larger size
        S = np.zeros(n)
        m = np.median(np.nan_to_num(_clim_scat_data[3]))

        if m < 1.0 or m > 10.0:
            S[...] = _clim_scat_data[3] * (1.0/m)
        else:
            S[...] = _clim_scat_data[3]

        scatter_color = Color(self.options_widget.true_color, self.options_widget.opacity/100.0)

        # Reset the data for scatter visual display
        self.scat_visual.set_data(P, symbol='disc', edge_color=None, face_color=scatter_color, size=S)
        self.canvas.update()
        # self.scat_data = [P, scatter_color, S]

    def update_clim(self):
        array = self.components[4]

        self.options_widget.cmin = "%.4g" % np.nanmin(array)
        self.options_widget.cmax = "%.4g" % np.nanmax(array)

    def clim_for_scat_data(self, clim_filter):
        clim_scat_data = []
        for idx in range(3):
            each_com = self.scat_data_refresh[0][:, idx]
            clim_scat_data.append(each_com[clim_filter])
        S = self.scat_data_refresh[2]
        clim_scat_data.append(S[clim_filter])
        return clim_scat_data

    def get_minmax(self, array):
        return float("%.4g" % np.nanmin(array)), float("%.4g" % np.nanmax(array))

    # Set the transform of visual&axis and distance of turntable camera according to the scale of the data
    def set_transform(self, position, size):
        # Get the min and max of each axis
        xmin, xmax = self.get_minmax(position[0])
        ymin, ymax = self.get_minmax(position[1])
        zmin, zmax = self.get_minmax(position[2])
        sizemin, sizemax = self.get_minmax(size)
        _axis_scale = (sizemax ** (1. / 3) / 1.e1, sizemax ** (1. / 3) / 1.e1, sizemax ** (1. / 3) / 1.e1)
        trans = (-(xmax+xmin)/2.0, -(ymax+ymin)/2.0, -(zmax+zmin)/2.0)
        self.scat_visual.transform = scene.STTransform(translate=trans)
        max_dis = np.nanmax([(xmax-xmin)/2.0, (ymax-ymin)/2.0, (zmax-zmin)/2.0])

        self.turn_cam.fov = 30.0
        self.turn_cam.distance = tan(radians(90.0-self.turn_cam.fov/2.0))*float(max_dis)

        self.axis.transform = scene.STTransform(scale=_axis_scale)

        self.trans_flag = 1


