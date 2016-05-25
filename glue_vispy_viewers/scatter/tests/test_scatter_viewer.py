from distutils.version import LooseVersion

import numpy as np

import glue
from glue.core import DataCollection, Data
from glue.app.qt.application import GlueApplication
from glue.core.component import Component

from matplotlib import cm

from ..scatter_viewer import VispyScatterViewer

GLUE_LT_08 = LooseVersion(glue.__version__) < LooseVersion('0.8')


def make_test_data():

    data = Data(label="Test Cat Data 1")

    np.random.seed(12345)

    for letter in 'abcdefxyz':
        comp = Component(np.random.random(100))
        data.add_component(comp, letter)

    return data


def test_scatter_viewer(tmpdir):

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data)
    scatter.viewer_size = (400, 500)

    options = scatter.options_widget()

    options.x_att = data.id['a']
    options.y_att = data.id['f']
    options.z_att = data.id['z']

    options.x_stretch = 0.5
    options.y_stretch = 1.0
    options.z_stretch = 2.0

    options.x_min = -0.1
    options.x_max = 1.1
    options.y_min = 0.1
    options.y_max = 0.9
    options.z_min = 0.2
    options.z_max = 0.8

    options.visible_box = False

    # Get layer artist style editor
    layer_artist = scatter.layers[0]
    style_widget = scatter._view.layout_style_widgets[layer_artist]

    style_widget.size_mode = 'Linear'
    style_widget.size_attribute = data.id['c']
    style_widget.size_scaling = 2
    style_widget.size_vmin = 0.2
    style_widget.size_vmax = 0.8

    style_widget.color_mode = 'Linear'
    style_widget.cmap_attribute = data.id['y']
    style_widget.cmap_vmin = 0.1
    style_widget.cmap_vmax = 0.9
    style_widget.cmap = cm.BuGn

    # Check that writing a session works as expected. However, this only
    # works with Glue 0.8 and above, so we skip this test if we are using an
    # older version.

    if GLUE_LT_08:
        return

    session_file = tmpdir.join('test_scatter_viewer.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    scatter_r = ga2.viewers[0][0]

    assert scatter_r.viewer_size == (400, 500)

    options = scatter_r.options_widget()

    assert options.x_att.label == 'a'
    assert options.y_att.label == 'f'
    assert options.z_att.label == 'z'

    assert options.x_stretch == 0.5
    assert options.y_stretch == 1.0
    assert options.z_stretch == 2.0

    assert options.x_min == -0.1
    assert options.x_max == 1.1
    assert options.y_min == 0.1
    assert options.y_max == 0.9
    assert options.z_min == 0.2
    assert options.z_max == 0.8

    assert not options.visible_box

    layer_artist = scatter_r.layers[0]

    assert layer_artist.size_mode == 'linear'
    assert layer_artist.size_attribute.label == 'c'
    np.testing.assert_allclose(layer_artist.size_scaling, 2, rtol=0.01)
    assert layer_artist.size_vmin == 0.2
    assert layer_artist.size_vmax == 0.8

    assert layer_artist.color_mode == 'linear'
    assert layer_artist.cmap_attribute.label == 'y'
    assert layer_artist.cmap_vmin == 0.1
    assert layer_artist.cmap_vmax == 0.9
    assert layer_artist.cmap is cm.BuGn


def test_n_dimensional_data():

    # Create fake data
    data = Data(x=np.random.random((2,3,4,5)),
                y=np.random.random((2,3,4,5)),
                z=np.random.random((2,3,4,5)))

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data)

    layer_artist = scatter.layers[0]
    style_widget = scatter._view.layout_style_widgets[layer_artist]

    style_widget.size_mode = 'Linear'
    style_widget.size_attribute = data.id['x']

    style_widget.color_mode = 'Linear'
    style_widget.cmap_attribute = data.id['y']
    style_widget.cmap = cm.BuGn

