from contextlib import contextmanager

import numpy as np

from matplotlib.colors import ColorConverter

from vispy import scene
from vispy.scene.visuals import Arrow


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
        self._error_vector_widget = None
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
                                  'errors': None,
                                  'vectors': None,
                                  'draw_arrows': False,
                                  'color': np.asarray((1., 1., 1.)),
                                  'alpha': 1.,
                                  'zorder': lambda: 0,
                                  'size': 10,
                                  'visible': True}

    def deallocate(self, label):
        self.layers.pop(label)
        self._update()

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

    def set_errors(self, label, error_lines):
        self.layers[label]['errors'] = error_lines
        self._update()

    def set_vectors(self, label, vectors):
        self.layers[label]['vectors'] = vectors
        self._update()

    def set_draw_arrows(self, label, draw_arrows):
        self.layers[label]['draw_arrows'] = draw_arrows
        self._update()

    def set_size(self, label, size):
        if not np.isscalar(size) and size.ndim > 1:
            raise Exception("size should be a 1-d array")
        self.layers[label]['size'] = size
        self._update()

    def set_color(self, label, rgb):
        if isinstance(rgb, str):
            rgb = ColorConverter().to_rgb(rgb)
        self.layers[label]['color'] = np.asarray(rgb)
        self._update()

    def set_alpha(self, label, alpha):
        self.layers[label]['alpha'] = alpha
        self._update()

    def set_zorder(self, label, zorder):
        self.layers[label]['zorder'] = zorder
        self._update()

    def update_line_width(self, width):
        if self._error_vector_widget:
            self._error_vector_widget.set_data(width=width)

    def _update(self):

        if self._skip_update:
            return

        data = []
        colors = []
        sizes = []
        lines = []
        line_colors = []
        arrows = []
        arrow_colors = []

        for label in sorted(self.layers, key=lambda x: self.layers[x]['zorder']()):

            layer = self.layers[label]

            if not layer['visible'] or layer['data'] is None:
                continue

            input_points = layer['data'].shape[0]
            if layer['mask'] is None:
                n_points = input_points
            else:
                n_points = np.sum(layer['mask'])

            if input_points > 0 and n_points > 0:

                # Data

                if layer['mask'] is None:
                    data.append(layer['data'])
                else:
                    data.append(layer['data'][layer['mask'], :])

                # Colors

                if layer['color'].ndim == 1:
                    rgba = np.hstack([layer['color'], 1])
                    rgba = np.repeat(rgba, n_points).reshape(4, -1).transpose()
                else:
                    if layer['mask'] is None:
                        rgba = layer['color'].copy()
                    else:
                        rgba = layer['color'][layer['mask']]

                rgba[:, 3] *= layer['alpha']

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

                # Error bar and colors
                if layer['errors'] is not None:
                    for error_set in layer['errors']:
                        if layer['mask'] is None:
                            out = error_set
                        else:
                            out = error_set[layer['mask']]
                        out = out.reshape((-1, 3))
                        lines.append(out)
                        line_colors.append(np.repeat(rgba, 2, axis=0))

                if layer['vectors'] is not None:
                    if layer['mask'] is None:
                        out = layer['vectors']
                    else:
                        out = layer['vectors'][layer['mask']]
                    lines.append(out.reshape((-1, 3)))
                    line_colors.append(np.repeat(rgba, 2, axis=0))
                    if layer['draw_arrows']:
                        arrows.append(out)
                        arrow_colors.append(rgba)

        if len(data) == 0:
            self.visible = False
            return
        else:
            self.visible = True

        data = np.vstack(data)
        colors = np.vstack(colors)
        sizes = np.hstack(sizes)

        self.set_data(data, edge_color=colors, face_color=colors, size=sizes)

        if len(lines) == 0:
            if self._error_vector_widget is not None:
                self._error_vector_widget.visible = False
            return
        else:
            if self._error_vector_widget is None:
                widget = Arrow(parent=self, connect="segments")
                widget.set_gl_state(depth_test=False, blend=True,
                                    blend_func=('src_alpha', 'one_minus_src_alpha'))
                self._error_vector_widget = widget
            self._error_vector_widget.visible = True

        lines = np.vstack(lines)
        line_colors = np.vstack(line_colors)
        self._error_vector_widget.set_data(pos=lines, color=line_colors)

        arrows = np.vstack(arrows) if len(arrows) > 0 else np.array([])
        arrow_colors = np.vstack(arrow_colors) if len(arrow_colors) else np.array([])
        self._error_vector_widget.set_data(arrows=arrows)
        self._error_vector_widget.arrow_color = arrow_colors

    def draw(self, *args, **kwargs):
        if len(self.layers) == 0:
            return
        else:
            try:
                super(MultiColorScatter, self).draw(*args, **kwargs)
            except Exception:
                pass


if __name__ == "__main__":  # pragma: nocover

    from vispy import app, scene

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
