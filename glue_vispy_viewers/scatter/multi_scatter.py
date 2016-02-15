from vispy import scene
from vispy.color import Color

from glue.external import six


class MultiColorScatter(scene.visuals.Markers):
    """
    This is a helper class to make it easier to show multiple markers at
    specific positions and control exactly which marker should be on top of
    which.
    """

    def __init__(self, *args, **kwargs):
        self.layers = {}
        self._combined_data = None
        super(MultiColorScatter, self).__init__(*args, **kwargs)

    def set_data_values(self, x, y, z):
        """
        Set the position of the datapoints
        """
        self._combined_data = np.array([x, y, z]).transpose()

    def allocate(self, label):
        if label in self.layers:
            raise ValueError("Layer {0} already exists".format(label))
        else:
            self.layers[label] = {'mask': None,
                                  'color': 'white',
                                  'alpha': 1,
                                  'zorder':0,
                                  'size': 10}

    def deallocate(self, label):
        self.layers.pop(label)

    def set_mask(self, label, mask):
        self.layers[label]['mask'] = mask
        self._update()

    def set_size(self, label, size):
        self.layers[label]['size'] = size
        self._update()

    def set_color(self, label, color):
        self.layers[label]['color'] = color
        self._update()

    def set_alpha(self, label, alpha):
        self.layers[label]['alpha'] = alpha
        self._update()

    def set_zorder(self, label, zorder):
        self.layers[label]['zorder'] = zorder
        self._update()

    def _update(self):

        data = []
        colors = []
        sizes = []

        for label in sorted(self.layers, key=lambda x: self.layers[x]['zorder']):

            layer = self.layers[label]

            if layer['mask'] is None:
                n_points = self._combined_data.shape[0]
            else:
                n_points = np.sum(layer['mask'])

            if n_points > 0:

                # Data

                if layer['mask'] is None:
                    data.append(self._combined_data)
                else:
                    data.append(self._combined_data[layer['mask'], :])

                # Colors

                if isinstance(layer['color'], six.string_types):
                    rgba = Color(layer['color']).rgba
                    rgba = np.repeat(rgba, n_points).reshape(4, -1).transpose()
                    rgba[:, 3] = layer['alpha']
                else:
                    raise TypeError("Only string colors supported for now")

                colors.append(rgba)

                # Sizes

                if np.isscalar(layer['size']):
                    size = np.repeat(layer['size'], n_points)
                else:
                    size = layer['size'][layer['mask']]

                sizes.append(size)

        data = np.vstack(data)
        colors = np.vstack(colors)
        sizes = np.hstack(sizes)

        self.set_data(data, edge_color=colors, face_color=colors, size=sizes)

    def draw(self, *args, **kwargs):
        if len(self.layers) == 0:
            return
        else:
            super(MultiColorScatter, self).draw(*args, **kwargs)


if __name__ == "__main__":

    from vispy import app, scene

    canvas = scene.SceneCanvas(keys='interactive')
    view = canvas.central_widget.add_view()
    view.camera = scene.TurntableCamera(up='z', fov=60)

    import numpy as np
    x = np.random.random(20)
    y = np.random.random(20)
    z = np.random.random(20)

    multi_scat = MultiColorScatter(parent=view.scene)
    multi_scat.set_data_values(x, y, z)

    multi_scat.allocate('data')
    multi_scat.set_zorder('data', 0)

    multi_scat.allocate('subset1')
    multi_scat.set_mask('subset1', np.random.random(20) > 0.5)
    multi_scat.set_color('subset1', 'red')
    multi_scat.set_zorder('subset1', 1)

    multi_scat.allocate('subset2')
    multi_scat.set_mask('subset2', np.random.random(20) > 0.5)
    multi_scat.set_color('subset2', 'green')
    multi_scat.set_zorder('subset2', 2)
    multi_scat.set_alpha('subset2', 0.5)
    multi_scat.set_size('subset2', 20)

    axis = scene.visuals.XYZAxis(parent=view.scene)

    canvas.show()
    app.run()
