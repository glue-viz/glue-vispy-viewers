import numpy as np

from ...extern.vispy import scene

from ..viewer_options import VispyOptionsWidget
from ..vispy_widget import VispyWidget


def test_vispy_widget():

    w = VispyWidget()
    d = VispyOptionsWidget(vispy_widget=w)

    w.show()
    d.show()

    # Try adding marker visuals to the scene
    positions = np.random.random((1000, 3))
    scat_visual = scene.visuals.Markers()
    scat_visual.set_data(positions, symbol='disc', edge_color=None, face_color='red')
    w.add_data_visual(scat_visual)

    d.set_limits(-1., 1., -1., 1., -1., 1.)

    np.testing.assert_equal(scat_visual.transform.scale, [1., 1., 1., 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [0., 0., 0., 0.])

    d.x_min = 0
    d.x_max = +1

    np.testing.assert_equal(scat_visual.transform.scale, [2., 1., 1., 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-1., 0., 0., 0.])

    d.y_min = 0.
    d.y_max = +2

    np.testing.assert_equal(scat_visual.transform.scale, [2., 1., 1., 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-1., -1., 0., 0.])

    d.z_min = -8
    d.z_max = +0

    np.testing.assert_equal(scat_visual.transform.scale, [2., 1., 0.25, 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-1, -1., 1., 0.])

    d.x_stretch = 10

    np.testing.assert_equal(scat_visual.transform.scale, [20., 1., 0.25, 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-10, -1., 1., 0.])

    d.y_stretch = 5

    np.testing.assert_equal(scat_visual.transform.scale, [20., 5., 0.25, 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-10, -5., 1., 0.])

    d.z_stretch = 4

    np.testing.assert_equal(scat_visual.transform.scale, [20., 5., 1, 1.])
    np.testing.assert_equal(scat_visual.transform.translate, [-10, -5., 4., 0.])
