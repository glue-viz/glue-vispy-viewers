from vispy import scene
from vispy.visuals.transforms import STTransform, ChainTransform

from glue_vispy_viewers.compat.axis import Axis

import numpy as np


class AxesVisual3D(object):

    def __init__(self, view=None, transform=None, **kwargs):

        self.view = view

        # Add a 3D cube to show us the unit cube. The 1.001 factor is to make
        # sure that the grid lines are not 'hidden' by volume renderings on the
        # front side due to numerical precision.
        cube_verts = np.array([[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
                               [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]])
        cube_edge_indices = np.array([[0, 1], [0, 3], [0, 5], [1, 2], [1, 6], [2, 3],
                                      [2, 7], [3, 4], [4, 5], [4, 7], [5, 6], [6, 7]])
        self.axis = scene.visuals.Line(cube_verts, parent=self.view.scene,
                                       color=kwargs['axis_color'], connect=cube_edge_indices)

        self.axis.transform = transform

        self.xax = Axis(pos=[[-1.0, 0], [1.0, 0]],
                        tick_direction=(0, -1),
                        parent=self.view.scene, axis_label='X',
                        anchors=['center', 'middle'], **kwargs)

        self.yax = Axis(pos=[[0, -1.0], [0, 1.0]],
                        tick_direction=(-1, 0),
                        parent=self.view.scene, axis_label='Y',
                        anchors=['center', 'middle'], **kwargs)

        self.zax = Axis(pos=[[0, -1.0], [0, 1.0]],
                        tick_direction=(-1, 0),
                        parent=self.view.scene, axis_label='Z',
                        anchors=['center', 'middle'], **kwargs)

        self.xtr = STTransform()
        self.xtr = self.xtr.as_matrix()
        self.xtr.rotate(45, (1, 0, 0))
        self.xtr.translate((0, -1., -1.))

        self.ytr = STTransform()
        self.ytr = self.ytr.as_matrix()
        self.ytr.rotate(-45, (0, 1, 0))
        self.ytr.translate((-1, 0, -1.))

        self.ztr = STTransform()
        self.ztr = self.ztr.as_matrix()
        self.ztr.rotate(45, (0, 1, 0))
        self.ztr.rotate(90, (1, 0, 0))
        self.ztr.translate((-1, -1, 0.))

        self.xax.transform = ChainTransform(transform, self.xtr)
        self.yax.transform = ChainTransform(transform, self.ytr)
        self.zax.transform = ChainTransform(transform, self.ztr)

    @property
    def tick_color(self):
        return self.xax.tick_color

    @tick_color.setter
    def tick_color(self, value):
        self.xax.tick_color = value
        self.yax.tick_color = value
        self.zax.tick_color = value

    @property
    def label_color(self):
        return self._label_color

    @label_color.setter
    def label_color(self, value):
        self.xax.label_color = value
        self.yax.label_color = value
        self.zax.label_color = value

    @property
    def axis_color(self):
        return self._axis_color

    @axis_color.setter
    def axis_color(self, value):
        self.axis.set_data(color=value)

    @property
    def tick_font_size(self):
        return self.xax.tick_font_size

    @tick_font_size.setter
    def tick_font_size(self, value):
        self.xax.tick_font_size = value
        self.yax.tick_font_size = value
        self.zax.tick_font_size = value

    @property
    def axis_font_size(self):
        return self.xax.axis_font_size

    @axis_font_size.setter
    def axis_font_size(self, value):
        self.xax.axis_font_size = value
        self.yax.axis_font_size = value
        self.zax.axis_font_size = value

    @property
    def xlabel(self):
        return self.xax.axis_label

    @xlabel.setter
    def xlabel(self, value):
        self.xax.axis_label = value

    @property
    def ylabel(self):
        return self.yax.axis_label

    @ylabel.setter
    def ylabel(self, value):
        self.yax.axis_label = value

    @property
    def zlabel(self):
        return self.zax.axis_label

    @zlabel.setter
    def zlabel(self, value):
        self.zax.axis_label = value

    @property
    def xlim(self):
        return self.xax.domain

    @xlim.setter
    def xlim(self, value):
        self.xax.domain = value

    @property
    def ylim(self):
        return self.yax.domain

    @ylim.setter
    def ylim(self, value):
        self.yax.domain = value

    @property
    def zlim(self):
        return self.zax.domain

    @zlim.setter
    def zlim(self, value):
        self.zax.domain = value

    @property
    def parent(self):
        return self.axis.parent

    @parent.setter
    def parent(self, value):
        self.axis.parent = value
        self.xax.parent = value
        self.yax.parent = value
        self.zax.parent = value
