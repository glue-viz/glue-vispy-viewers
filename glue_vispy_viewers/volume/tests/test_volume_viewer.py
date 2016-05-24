from distutils.version import LooseVersion

import numpy as np

import glue
from glue.core import DataCollection, Data
from glue.app.qt.application import GlueApplication
from glue.core.component import Component

from ..volume_viewer import VispyVolumeViewer

GLUE_LT_08 = LooseVersion(glue.__version__) < LooseVersion('0.8')


def make_test_data():

    data = Data(label="Test Cube Data")

    np.random.seed(12345)

    for letter in 'abc':
        comp = Component(np.random.random((10, 10, 10)))
        data.add_component(comp, letter)

    return data


def test_volume_viewer(tmpdir):

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data)
    volume.viewer_size = (400, 500)

    options = volume.options_widget()

    options.x_stretch = 0.5
    options.y_stretch = 1.0
    options.z_stretch = 2.0

    options.x_min = -0.1
    options.x_max = 10.1
    options.y_min = 0.1
    options.y_max = 10.9
    options.z_min = 0.2
    options.z_max = 10.8

    options.visible_box = False

    # Get layer artist style editor
    layer_artist = volume.layers[0]
    style_widget = volume._view.layout_style_widgets[layer_artist]

    style_widget.attribute = data.id['b']
    style_widget.vmin = 0.1
    style_widget.vmax = 0.9
    style_widget.alpha = 0.8

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_volume_viewer.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    volume_r = ga2.viewers[0][0]

    assert volume_r.viewer_size == (400, 500)

    options = volume_r.options_widget()

    assert options.x_stretch == 0.5
    assert options.y_stretch == 1.0
    assert options.z_stretch == 2.0

    assert options.x_min == -0.1
    assert options.x_max == 10.1
    assert options.y_min == 0.1
    assert options.y_max == 10.9
    assert options.z_min == 0.2
    assert options.z_max == 10.8

    assert not options.visible_box

    layer_artist = volume_r.layers[0]

    assert style_widget.attribute.label == 'b'
    assert style_widget.vmin == 0.1
    assert style_widget.vmax == 0.9
    assert style_widget.alpha == 0.8

    ga2.close()
