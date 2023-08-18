import numpy as np
import pytest
import sys

from glue.core import DataCollection, Data
from glue_qt.app.application import GlueApplication
from glue.core.component import Component

from matplotlib import cm

from ..scatter_viewer import VispyScatterViewer

IS_WIN = sys.platform == 'win32'


def make_test_data():

    data = Data(label="Test Cat Data 1")

    np.random.seed(12345)

    for letter in 'abcdefxyz':
        comp = Component(np.random.random(100))
        data.add_component(comp, letter)

    return data


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
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

    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_error_bars(tmpdir):

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

    layer_state = viewer_state.layers[0]

    layer_state.xerr_visible = True
    layer_state.xerr_attribute = data.id['b']

    layer_state.yerr_visible = False
    layer_state.yerr_attribute = data.id['c']

    layer_state.zerr_visible = True
    layer_state.zerr_attribute = data.id['d']

    assert viewer_state.line_width == 1

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_error_bars.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    scatter_r = ga2.viewers[0][0]
    layer_state = scatter_r.state.layers[0]

    assert layer_state.xerr_visible
    assert layer_state.xerr_attribute.label == 'b'

    assert not layer_state.yerr_visible
    assert layer_state.yerr_attribute.label == 'c'

    assert layer_state.zerr_visible
    assert layer_state.zerr_attribute.label == 'd'

    assert scatter_r.state.line_width == 1

    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_vectors(tmpdir):

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

    layer_state = viewer_state.layers[0]

    layer_state.vector_visible = True
    layer_state.vx_attribute = data.id['x']
    layer_state.vy_attribute = data.id['y']
    layer_state.vz_attribute = data.id['e']
    layer_state.vector_scaling = 0.1
    layer_state.vector_origin = 'tail'
    layer_state.vector_arrowhead = True

    viewer_state.line_width = 3

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_vectors.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    scatter_r = ga2.viewers[0][0]
    layer_state = scatter_r.state.layers[0]

    assert layer_state.vector_visible

    assert layer_state.vx_attribute.label == 'x'
    assert layer_state.vy_attribute.label == 'y'
    assert layer_state.vz_attribute.label == 'e'

    assert np.isclose(layer_state.vector_scaling, 0.1)

    assert layer_state.vector_origin == 'tail'

    assert layer_state.vector_arrowhead

    assert scatter_r.state.line_width == 3

    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
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

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
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
    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_add_data_with_incompatible_subsets(tmpdir):

    # Regression test for a bug that an error when adding a dataset with an
    # incompatible subset to a 3D scatter viewer.

    data1 = Data(label="Data 1", x=[1, 2, 3])
    data2 = Data(label="Data 2", y=[4, 5, 6])

    dc = DataCollection([data1, data2])
    ga = GlueApplication(dc)
    ga.show()

    # Subset is defined in terms of data2, so it's an incompatible subset
    # for data1
    dc.new_subset_group(subset_state=data2.id['y'] > 0.5, label='subset 1')

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data1)

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_not_all_points_inside_limits(tmpdir):

    # Regression test for a bug that occurred when not all points were inside
    # the visible limits and the color or size mode is linear.

    data1 = Data(label="Data", x=[1, 2, 3])

    dc = DataCollection([data1])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data1)

    scatter.state.layers[0].color_mode = 'Linear'
    scatter.state.layers[0].size_mode = 'Linear'

    scatter.state.x_min = -0.1
    scatter.state.x_max = 2.1

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_categorical_color_size(tmpdir):

    # Create fake data
    data = make_test_data()

    # Add categorical component
    data['categorical'] = ['a', 'b'] * 50

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data)

    viewer_state = scatter.state

    viewer_state.x_att = data.id['a']
    viewer_state.y_att = data.id['b']
    viewer_state.z_att = data.id['z']

    layer_state = viewer_state.layers[0]

    layer_state.size_mode = 'Linear'
    layer_state.size_attribute = data.id['categorical']

    layer_state.color_mode = 'Linear'
    layer_state.cmap_attribute = data.id['categorical']

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_layer_visibility_after_session(tmpdir):

    # Regression test for a bug that caused layers to be incorrectly visible
    # after saving and loading a session file.

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    scatter = ga.new_data_viewer(VispyScatterViewer)
    scatter.add_data(data)

    viewer_state = scatter.state
    layer_state = viewer_state.layers[0]
    layer_state.visible = False

    session_file = tmpdir.join('test_layer_visibility.glu').strpath
    ga.save_session(session_file)
    ga.close()

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    scatter_r = ga2.viewers[0][0]
    viewer_state = scatter_r.state
    layer_state = viewer_state.layers[0]
    assert not layer_state.visible

    # Make sure the multiscat layer is also not visible (this was where the bug was)
    layer_artist = scatter_r.layers[0]
    assert not layer_artist._multiscat.layers[layer_artist.id]['visible']

    ga2.close()
