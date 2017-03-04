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

    viewer_state = scatter.state

    viewer_state.x_att = data.id['a']
    viewer_state.y_att = data.id['f']
    viewer_state.z_att = data.id['z']

    viewer_state.x_stretch = 0.5
    viewer_state.y_stretch = 1.0
    viewer_state.z_stretch = 2.0

    viewer_state.x_min = -0.1
    viewer_state.x_max = 1.1
    viewer_state.y_min = 0.1
    viewer_state.y_max = 0.9
    viewer_state.z_min = 0.2
    viewer_state.z_max = 0.8

    viewer_state.visible_axes = False

    # Get layer artist style editor
    layer_state = viewer_state.layers[0]

    layer_state.size_attribute = data.id['c']
    layer_state.size_mode = 'Linear'
    layer_state.size_scaling = 2
    layer_state.size_vmin = 0.2
    layer_state.size_vmax = 0.8

    layer_state.cmap_attribute = data.id['y']
    layer_state.color_mode = 'Linear'
    layer_state.cmap_vmin = 0.1
    layer_state.cmap_vmax = 0.9
    layer_state.cmap = cm.BuGn

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_scatter_viewer.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    scatter_r = ga2.viewers[0][0]

    assert scatter_r.viewer_size == (400, 500)

    viewer_state = scatter_r.state

    assert viewer_state.x_att.label == 'a'
    assert viewer_state.y_att.label == 'f'
    assert viewer_state.z_att.label == 'z'

    np.testing.assert_allclose(viewer_state.x_stretch, 0.5, rtol=1e-3)
    np.testing.assert_allclose(viewer_state.y_stretch, 1.0, rtol=1e-3)
    np.testing.assert_allclose(viewer_state.z_stretch, 2.0, rtol=1e-3)

    assert viewer_state.x_min == -0.1
    assert viewer_state.x_max == 1.1
    assert viewer_state.y_min == 0.1
    assert viewer_state.y_max == 0.9
    assert viewer_state.z_min == 0.2
    assert viewer_state.z_max == 0.8

    assert not viewer_state.visible_axes

    layer_state = viewer_state.layers[0]

    assert layer_state.size_mode == 'Linear'
    assert layer_state.size_attribute.label == 'c'
    np.testing.assert_allclose(layer_state.size_scaling, 2, rtol=0.01)
    assert layer_state.size_vmin == 0.2
    assert layer_state.size_vmax == 0.8

    assert layer_state.color_mode == 'Linear'
    assert layer_state.cmap_attribute.label == 'y'
    assert layer_state.cmap_vmin == 0.1
    assert layer_state.cmap_vmax == 0.9
    assert layer_state.cmap is cm.BuGn


def test_n_dimensional_data():

    # Create fake data
    data = Data(x=np.random.random((2, 3, 4, 5)),
                y=np.random.random((2, 3, 4, 5)),
                z=np.random.random((2, 3, 4, 5)))

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


def test_scatter_remove_layer_artists(tmpdir):

    # Regression test for a bug that caused layer states to not be removed
    # when the matching layer artist was removed. This then caused issues when
    # loading session files.

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data)

    dc.new_subset_group(subset_state=data.id['x'] > 0.5, label='subset 1')

    scatter.add_subset(data.subsets[0])

    assert len(scatter.layers) == 2
    assert len(scatter.state.layers) == 2

    dc.remove_subset_group(dc.subset_groups[0])

    assert len(scatter.layers) == 1
    assert len(scatter.state.layers) == 1

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_scatter_viewer.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()
