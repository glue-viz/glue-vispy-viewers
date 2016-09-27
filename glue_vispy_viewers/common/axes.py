from ..extern.vispy import scene
from ..extern.vispy.geometry import create_cube
from ..extern.vispy.visuals.transforms import STTransform, ChainTransform


class AxesVisual3D(object):

    def __init__(self, view=None, transform=None, **kwargs):

        self.view = view

        # Add a 3D cube to show us the unit cube. The 1.001 factor is to make
        # sure that the grid lines are not 'hidden' by volume renderings on the
        # front side due to numerical precision.
        vertices, filled_indices, outline_indices = create_cube()
        self.axis = scene.visuals.Mesh(vertices['position'],
                                       outline_indices, parent=self.view.scene,
                                       color=kwargs['axis_color'], mode='lines')

        self.axis.transform = transform

        self.xax = scene.visuals.Axis(pos=[[-1.0, 0], [1.0, 0]],
                                      tick_direction=(0, -1),
                                      parent=self.view.scene, axis_label='X',
                                      anchors=['center', 'middle'], **kwargs)

        self.yax = scene.visuals.Axis(pos=[[0, -1.0], [0, 1.0]],
                                      tick_direction=(-1, 0),
                                      parent=self.view.scene, axis_label='Y',
                                      anchors=['center', 'middle'], **kwargs)

        self.zax = scene.visuals.Axis(pos=[[0, -1.0], [0, 1.0]],
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
