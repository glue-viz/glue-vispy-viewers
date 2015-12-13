from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app
from vispy.color import get_colormap, Color
from math import cos, sin, asin, radians, degrees
from vispy.scene.cameras import MagnifyCamera, Magnify1DCamera

from vispy.visuals import transforms


__all__ = ['QtScatVispyWidget']

# TODO : create a custom visual inherited from Markers
class QtScatVispyWidget(QtGui.QWidget):
    def __init__(self, parent=None):

        super(QtScatVispyWidget, self).__init__(parent=parent)

        # Prepare canvas
        self.canvas = scene.SceneCanvas(keys='interactive', show=False)
        self.canvas.measure_fps()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.canvas.central_widget.add_view()
        self.view.border_color = 'red'
        self.view.parent = self.canvas.scene
        self.turn_cam = scene.cameras.TurntableCamera(parent=self.view.scene, name='Turntable')
        self.mag_cam = MagnifyCamera()
        self.view.camera = self.turn_cam # or try 'arcball'

        self.data = None
        self.axes_names = None
        self._current_array = None

        # create scatter object and fill in the data
        self.scatter = scene.visuals.Markers()

        # Add a grid plane
        # The pos of the visual will be at the center of the parent !
        a = 400 - self.canvas.size[0]/2.0
        b = 300 - self.canvas.size[1]/2.0
        self.grid = scene.visuals.GridLines(scale=(0.5, 0.5), parent=self.view)

        # Try to set the center of grid identical with the censer of the axis
        # But found not so necessary now
        # self.grid.transform = transforms.STTransform(translate=(a, b))

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)
        print('==========')
        print('canvas size', self.canvas.size)
        self.widget_axis_scale = [1, 1, 1]

        # trans.scale = self.axis.transform.scale

        self._shown_data = None
        self.canvas.events.resize.connect(self.on_resize)

    def add_fila(self):
        vol = np.genfromtxt('/Users/penny/Works/filaments_vispy/Penny_Bones_Updated.txt', delimiter='\t', dtype=None)
        fila = []
        # fila's structure is [filament_name, glong, glat, gdistance_kpc, radius_pc]
        for n in np.arange(0, vol.shape[0], 1):
            fila.append([vol[n][0], vol[n][1], vol[n][2], vol[n][3], vol[n][4]])
        filament_name = []
        filament_name.append(vol[0][0])
        i=0
        points = []
        one_fila = []
        new_fila = []
        # Sort the lbd data through longitude
        for each_line in fila:
            if each_line[0] == filament_name[i]:
                one_fila.append(each_line)
            else:
                sort_fila = np.sort(one_fila, axis=0)
                new_fila.append(sort_fila)
                one_fila = []
                one_fila.append(each_line)
                i=i+1
                filament_name.append(each_line[0])
        sort_fila = np.sort(one_fila, axis=0)
        new_fila.append(sort_fila)

        i = 0
        new_filament_name = []
        new_filament_name.append(vol[0][0])

        for each_fila in new_fila:
            for each_new_line in each_fila:
                if each_new_line[0] == new_filament_name[i]:
                    l=radians(float(each_new_line[1]))
                    b=radians(float(each_new_line[2]))
                    d=float(each_new_line[3])
                    points.append([d*cos(l)*cos(b), d*sin(l)*cos(b), d*sin(b)])
                    # Sort the points according to the first dimension
                    radius = float(each_new_line[4])/100.0
                else:
                    l = scene.visuals.Tube(points,
                                    color='yellow',
                                    shading='flat',
                                    tube_points=8,
                                    radius=float(radius))
                    '''print('=========')
                    print('radius:', radius)
                    print('sort_points:', sort_points)'''
                    self.view.add(l)
                    points = []
                    l=radians(float(each_new_line[1]))
                    b=radians(float(each_new_line[2]))
                    d=float(each_new_line[3])
                    points.append([d*cos(l)*cos(b), d*sin(l)*cos(b), d*sin(b)])
                    # redefine the points
                    i=i+1
                    new_filament_name.append(each_new_line[0])
        # Draw points
        l = scene.visuals.Tube(points,
                        color='yellow',
                        shading='flat',
                        tube_points=8,
                        radius=float(radius))
        self.view.add(l)
        self.canvas.update()

    def on_resize(self, event):
        # TODO: resize of the grid?

        a = 400 - self.canvas.size[0]/2.0
        b = 300 - self.canvas.size[1]/2.0
        # self.grid.transform = transforms.STTransform(translate=(a, b))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if data is None:
            self._data = data
        else:
            self._data = data
            first_data = data[data.components[0]]
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

    # For better get the component for clim dataset
    def clim_components(self, clim_filter):
        if self.components is None:
            return None
        else:
            clim_components = []
            for each_com in self.components:
                clim_components.append(each_com[clim_filter])
            return clim_components

    def _refresh(self):
        """
        This method can be called if the options widget is updated.
        """
        if self.data is None:
            return
            array = self.component
            self.update()

    def set_subsets(self, subsets):
        self.subsets = subsets

    def set_program(self):
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

            # Dot size determination according to the mass - *2 for larger size
            S = np.zeros(n)
            # size = np.ones((n, 1))
            # size[:, 0] = self.components[3]
            S[...] = self.components[3] ** (1. / 3) / 1.e1


            scatter_color =Color(self.options_widget.true_color, self.options_widget.opacity/100.0)

            # Set default color = 'gold'
            print('=============')
            print('scatter_color is', scatter_color)
            print('=============')

            self.scatter.set_data(P, symbol='disc', edge_color=None, face_color=scatter_color, size=S)
            self.view.add(self.scatter)

            # set clim value
            self._update_clim()
            self.canvas.update()

    # Set the clim dataset and apply the new dataset to the current scatter visual
    # TODO: add more clim options? Now the user could only clim one property
    def apply_clim(self):

        currentid = self.options_widget.ui.ClimComboBox.currentText()
        _clim_pro = self.data[currentid]

        # self.options_widget.cmin is in unicode type
        _cmin = float(self.options_widget.cmin)
        _cmax = float(self.options_widget.cmax)

        # Get new clim_components according to the filter
        more = _clim_pro > _cmin
        less = _clim_pro < _cmax
        clim_filter = np.all([more, less], axis=0)
        _clim_components = self.clim_components(clim_filter)

        n = len(_clim_components[0])
        P = np.zeros((n, 3), dtype=np.float32)

        X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
        X[...] = _clim_components[0]
        Y[...] = _clim_components[1]
        Z[...] = _clim_components[2]

        # Dot size determination according to the mass - *2 for larger size
        S = np.zeros(n)
        S[...] = _clim_components[3] ** (1. / 3) / 1.e1
        scatter_color =Color(self.options_widget.true_color, self.options_widget.opacity/100.0)

        # Reset the data for scatter visual display
        self.scatter.set_data(P, symbol='disc', edge_color=None, face_color=scatter_color, size=S)
        self.canvas.update()

    def _update_clim(self):
        array = self.components[4]

        self.options_widget.cmin = "%.4g" % np.nanmin(array)
        self.options_widget.cmax = "%.4g" % np.nanmax(array)

