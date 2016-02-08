from __future__ import absolute_import, division, print_function

import numpy as np
from glue.external.qt import QtGui
from vispy import scene
from vispy.color import Color
from math import radians, tan

from matplotlib.colors import ColorConverter
converter = ColorConverter()

from matplotlib.colors import ColorConverter
converter = ColorConverter()

__all__ = ['QtScatVispyWidget']

# TODO : instead of using customized colormap and opacity, use 'double click' on the left top panel
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
        self.scat_data = None

        self.scatter_color = None

        self._subset_changed = False
        self.subsets = []

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
            # self.data = np.nan_to_num(self.data)
            components = [self.data[self.options_widget.ui.xAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.yAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.zAxisComboBox.currentText()],
                          self.data[self.options_widget.ui.SizeComboBox.currentText()],
                          self.data[self.options_widget.ui.ClimComboBox.currentText()]]
            return components

    # TODO: not all subsets be removed, a few left & when set_subsets be called
    def set_subsets(self, subsets):
        self.subsets = subsets
        self._subset_changed = True
        print('subset.shape', self.subsets)
        self._refresh()

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

            # Normalize the sizes so that it falls into [1:20], as this range achieves optimal rendering
            S = np.zeros(n)
            S[...] = np.abs(np.nan_to_num(self.components[3])) ** (1.0/3)
            S = (S-np.min(S)) / (np.max(S)-np.min(S)) # normalize to [0,1]
            S[np.isneginf(S)] = 0
            S[np.isinf(S)] = 0
            S *= 20.0/np.max(S)

            self.scatter_color = np.ones((n, 4), dtype=np.float32)
            alpha = self.options_widget.opacity/100.0
            for idx in range(n):
                    self.scatter_color[idx] = Color(self.options_widget.true_color, alpha).rgba
            scat_visual = scene.visuals.Markers()
            scat_visual.set_data(P, symbol='disc', edge_color=None, face_color=self.scatter_color, size=S)
            self.scat_visual = scat_visual

            # Save scatter data for update
            self.scat_data = [P, self.scatter_color, S]
            self.view.add(self.scat_visual)

            if self.trans_flag == 0:
                # Set transform for axis and camera
                self.set_transform([self.components[0], self.components[1], self.components[2]], self.components[3])

            print('--------')
            print('n in addvisual is', n)
            self._update_clim()
            self.canvas.update()

    def update_scatter_visual(self, pos, color, size, symbol='disc'):
        """
        This method is called when basic properties for scatter visual got updated
        """
        self.scat_visual.set_data(pos, symbol=symbol, edge_color=None, face_color=color, size=size)
        self.set_transform([pos[:, 0], pos[:, 1], pos[:, 2]], size)
        self.canvas.update()

    def _refresh(self):
        """
        This method can be called if the sliders & clim got changed
        """
        if self.data is None:
            return

        if self.scat_visual is not None:
            # Add clim here
            currentid = self.options_widget.ui.ClimComboBox.currentText()
            _clim_pro = self.data[currentid]

            if self.options_widget.cmin == 'auto' or self.options_widget.cmax == 'auto':
                self._update_clim()

            # self.options_widget.cmin is in unicode type
            _cmin = float(self.options_widget.cmin)
            _cmax = float(self.options_widget.cmax)

            # Get new clim_components according to the filter
            more = _clim_pro >= _cmin
            less = _clim_pro <= _cmax
            print('more and less', more, less)
            # more and less [ True  True  True ...,  True  True  True] [ True  True  True ...,  True  True  True]
            clim_filter = np.all([more, less], axis=0)

            # Stretch control here
            stretch_scale = self.options_widget.stretch
            n = len(self.components[0])
            P = np.zeros((n, 3), dtype=np.float32)

            print('compare the lenth of data and after clim:', len(self.components[3]), n)
            for idx in range(3):
                P[:, idx] = self.components[idx] * stretch_scale[idx]

            # Normalize the sizes so that it falls into [1:20], as this range achieves optimal rendering
            S = np.zeros(n)
            S[...] = np.abs(np.nan_to_num(self.components[3])) ** (1.0/3)
            S = (S-np.min(S)) / (np.max(S)-np.min(S)) # normalize to [0,1]
            S[np.isneginf(S)] = 0
            S[np.isinf(S)] = 0
            S = S * 20.0/np.max(S) * stretch_scale[3]

            # Instead of moving those clim points from the dataset, here set the size of them to 0
            np.place(S, np.logical_not(clim_filter), 0)

            alpha = self.options_widget.opacity/100.0
            color = np.array(Color(self.options_widget.true_color, alpha).hex)

            if self._subset_changed:
                self._subset_changed = False
                for isubset, subset in enumerate(self.subsets):
                    # if the mask is all fault (newly created subset), then continue
                    mask = subset['mask']
                    if not any(mask):
                        continue
                    highlight_color = subset['color']
                    color_array = np.reshape(np.repeat(color, len(mask), axis=0), len(mask))
                    np.place(color_array, mask, highlight_color)

                    # Calculating an weighted averaging of mixed color, blend using alpha (opacity)
                    fg_color = np.ones((n, 4), dtype=np.float32)
                    for idx in range(n):
                        fg_color[idx] = Color(color_array[idx]).rgba
                    # Set the alpha of those unmasked points as 0
                    np.place(fg_color[:, 3], np.logical_not(mask), 0.0)
                    bg_color = self.scatter_color
                    re_color = np.ones((n, 4), dtype=np.float32) # result color
                    re_color[:, 3] = 1.0 - (1.0 - bg_color[:, 3]) * (1.0 - fg_color[:, 3])  # composite opacity

                    re_color[:, 0] = fg_color[:, 0] * fg_color[:, 3] / re_color[:, 3] + bg_color[:, 0] * (1 - fg_color[:, 3]) / re_color[:, 3]
                    re_color[:, 1] = fg_color[:, 1] * fg_color[:, 3] / re_color[:, 3] + bg_color[:, 1] * (1 - fg_color[:, 3]) / re_color[:, 3]
                    re_color[:, 2] = fg_color[:, 2] * fg_color[:, 3] / re_color[:, 3] + bg_color[:, 2] * (1 - fg_color[:, 3]) / re_color[:, 3]
                    self.scatter_color = re_color

            print(self.scatter_color)
            # Enable the opacity
            self.scatter_color[:, 3] = alpha

            self.update_scatter_visual(P, self.scatter_color, S)

    def _update_clim(self):
        array = self.components[4]
        self.options_widget.cmin = "%.4g" % np.nanmin(array)
        self.options_widget.cmax = "%.4g" % np.nanmax(array)

    def get_min_and_max(self, array):
        return float("%.4g" % np.nanmin(array)), float("%.4g" % np.nanmax(array))

    # Set the transform of visual & axis and distance of turntable camera according to the scale of the data
    def set_transform(self, position, size):
        xmin, xmax = self.get_min_and_max(position[0])
        ymin, ymax = self.get_min_and_max(position[1])
        zmin, zmax = self.get_min_and_max(position[2])
        sizemin, sizemax = self.get_min_and_max(size)
        # TODO: set the center of the view as the 'mass of center'
        _axis_scale = (sizemax ** (1. / 3) / 1.e1, sizemax ** (1. / 3) / 1.e1, sizemax ** (1. / 3) / 1.e1)
        trans = (-(xmax+xmin)/2.0, -(ymax+ymin)/2.0, -(zmax+zmin)/2.0)
        self.scat_visual.transform = scene.STTransform(translate=trans)
        max_dis = np.nanmax([(xmax-xmin)/2.0, (ymax-ymin)/2.0, (zmax-zmin)/2.0])

        self.turn_cam.fov = 30.0
        self.turn_cam.distance = tan(radians(90.0-self.turn_cam.fov/2.0))*float(max_dis)

        self.axis.transform = scene.STTransform(scale=_axis_scale)

        self.trans_flag = 1


