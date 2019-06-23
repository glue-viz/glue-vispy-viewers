import numpy as np

from glue.core import DataCollection, Data
from glue.app.qt.application import GlueApplication
from glue.core.component import Component

from ..isosurface_viewer import VispyIsosurfaceViewer


def make_test_data():

    data = Data(label="Test Cube Data")

    np.random.seed(12345)

    for letter in 'abc':
        comp = Component(np.random.random((10, 10, 10)))
        data.add_component(comp, letter)

    return data


def test_isosurface_viewer(tmpdir):

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyIsosurfaceViewer)
    volume.add_data(data)
    volume.viewer_size = (400, 500)

    viewer_state = volume.state

    viewer_state.x_stretch = 0.5
    viewer_state.y_stretch = 1.0
    viewer_state.z_stretch = 2.0

    viewer_state.x_min = -0.1
    viewer_state.x_max = 10.1
    viewer_state.y_min = 0.1
    viewer_state.y_max = 10.9
    viewer_state.z_min = 0.2
    viewer_state.z_max = 10.8

    viewer_state.visible_axes = False

    # Get layer artist style editor
    layer_state = viewer_state.layers[0]

    layer_state.attribute = data.id['b']
    layer_state.level_low = 0.1
    layer_state.level_high = 0.9
    # layer_state.alpha = 0.8

    # test set label from slider
    layer_state.step = 5
    assert layer_state.step == 5.0

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_volume_viewer.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    volume_r = ga2.viewers[0][0]

    assert volume_r.viewer_size == (400, 500)

    viewer_state = volume_r.state

    np.testing.assert_allclose(viewer_state.x_stretch, 0.5, rtol=1e-3)
    np.testing.assert_allclose(viewer_state.y_stretch, 1.0, rtol=1e-3)
    np.testing.assert_allclose(viewer_state.z_stretch, 2.0, rtol=1e-3)

    assert viewer_state.x_min == -0.1
    assert viewer_state.x_max == 10.1
    assert viewer_state.y_min == 0.1
    assert viewer_state.y_max == 10.9
    assert viewer_state.z_min == 0.2
    assert viewer_state.z_max == 10.8

    assert not viewer_state.visible_axes

    layer_artist = viewer_state.layers[0]

    assert layer_artist.attribute.label == 'b'
    assert layer_artist.level_low == 0.1
    assert layer_artist.level_high == 0.9
    # assert layer_artist.alpha == 0.8
    assert layer_artist.step == 5

    ga2.close()
