from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app
from vispy.color import get_colormap

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
        self.view.camera = 'turntable'  # or try 'arcball'

        self.data = None
        self.axes_names = None
        self._current_array = None

        # create scatter object and fill in the data
        self.scatter = scene.visuals.Markers()

        # Add a 3D axis to keep us oriented
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.widget_axis_scale = [1, 1, 1]

        # Set up default colormap
        self.color_map = get_colormap('hot')

        self._shown_data = None

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
            self.scatter.set_data(P, symbol='disc', edge_color=None, face_color=(1, 1, 1, .5), size=S)
            self.view.add(self.scatter)

            # set clim value
            self._update_clim()
            self.canvas.update()

    def _update_clim(self):
        array = self.components[4]
        print('===========')
        print('array for component[4]', array)
        print('===========')
        self.options_widget.cmin = "%.4g" % np.nanmin(array)
        self.options_widget.cmax = "%.4g" % np.nanmax(array)

