from contextlib import contextmanager

import numpy as np

from matplotlib.colors import ColorConverter

from ..extern.vispy import scene

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
        self._skip_update = False
        super(MultiColorScatter, self).__init__(*args, **kwargs)

    @contextmanager
    def delay_update(self):
        self._skip_update = True
        yield
        self._skip_update = False

    def allocate(self, label):
        if label in self.layers:
            raise ValueError("Layer {0} already exists".format(label))
        else:
            self.layers[label] = {'data': None,
                                  'mask': None,
                                  'color': np.asarray((1, 1, 1)),
                                  'alpha': 1,
                                  'zorder': lambda: 0,
                                  'size': 10,
                                  'visible': True}

    def deallocate(self, label):
        self.layers.pop(label)

    def set_data_values(self, label, x, y, z):
        """
        Set the position of the datapoints
        """
        # TODO: avoid re-allocating an array every time
        self.layers[label]['data'] = np.array([x, y, z]).transpose()
        self._update()

    def set_visible(self, label, visible):
        self.layers[label]['visible'] = visible
        self._update()

    def set_mask(self, label, mask):
        self.layers[label]['mask'] = mask
        self._update()

    def set_size(self, label, size):
        if not np.isscalar(size) and size.ndim > 1:
            raise Exception("size should be a 1-d array")
        self.layers[label]['size'] = size
        self._update()

    def set_color(self, label, rgb):
        if isinstance(rgb, six.string_types):
            rgb = ColorConverter().to_rgb(rgb)
        self.layers[label]['color'] = np.asarray(rgb)
        self._update()

    def set_alpha(self, label, alpha):
        self.layers[label]['alpha'] = alpha
        self._update()

    def set_zorder(self, label, zorder):
        self.layers[label]['zorder'] = zorder
        self._update()

    def _update(self):

        if self._skip_update:
            return

        data = []
        colors = []
        sizes = []

        for label in sorted(self.layers, key=lambda x: self.layers[x]['zorder']()):

            layer = self.layers[label]

            if not layer['visible'] or layer['data'] is None:
                continue

            if layer['mask'] is None:
                n_points = layer['data'].shape[0]
            else:
                n_points = np.sum(layer['mask'])

            if n_points > 0:

                # Data

                if layer['mask'] is None:
                    data.append(layer['data'])
                else:
                    data.append(layer['data'][layer['mask'], :])

                # Colors

                if layer['color'].ndim == 1:
                    rgba = np.hstack([layer['color'], 0])
                    rgba = np.repeat(rgba, n_points).reshape(4, -1).transpose()
                else:
                    rgba = layer['color']
                rgba[:, 3] = layer['alpha']

                colors.append(rgba)

                # Sizes

                if np.isscalar(layer['size']):
                    size = np.repeat(layer['size'], n_points)
                else:
                    if layer['mask'] is None:
                        size = layer['size']
                    else:
                        size = layer['size'][layer['mask']]

                sizes.append(size)

        if len(data) == 0:
            return

        data = np.vstack(data)
        colors = np.vstack(colors)
        sizes = np.hstack(sizes)

        self.set_data(data, edge_color=colors, face_color=colors, size=sizes)

    def draw(self, *args, **kwargs):
        if len(self.layers) == 0:
            return
        else:
            try:
                super(MultiColorScatter, self).draw(*args, **kwargs)
            except:
                pass


if __name__ == "__main__":

    from ..extern.vispy import app, scene

    canvas = scene.SceneCanvas(keys='interactive')
    view = canvas.central_widget.add_view()
    view.camera = scene.TurntableCamera(up='z', fov=60)

    x = np.random.random(20)
    y = np.random.random(20)
    z = np.random.random(20)

    multi_scat = MultiColorScatter(parent=view.scene)
    multi_scat.allocate('data')
    multi_scat.set_zorder('data', lambda: 0)
    multi_scat.set_data_values('data', x, y, z)

    multi_scat.allocate('subset1')
    multi_scat.set_mask('subset1', np.random.random(20) > 0.5)
    multi_scat.set_color('subset1', 'red')
    multi_scat.set_zorder('subset1', lambda: 1)

    multi_scat.allocate('subset2')
    multi_scat.set_mask('subset2', np.random.random(20) > 0.5)
    multi_scat.set_color('subset2', 'green')
    multi_scat.set_zorder('subset2', lambda: 2)
    multi_scat.set_alpha('subset2', 0.5)
    multi_scat.set_size('subset2', 20)

    axis = scene.visuals.XYZAxis(parent=view.scene)

    canvas.show()
    app.run()
