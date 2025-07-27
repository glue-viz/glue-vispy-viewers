import sys
import pytest
import numpy as np
from string import ascii_lowercase

from glue.config import colormaps
from glue.core import DataCollection, Data
from glue_qt.app.application import GlueApplication
from glue.core.component import Component
from glue.core.link_helpers import LinkSame

from ...layer_artist import DataProxy
from ..volume_viewer import VispyVolumeViewer

IS_WIN = sys.platform == 'win32'


def make_test_data(dimensions=(10, 10, 10)):

    data = Data(label="Test Cube Data")

    np.random.seed(12345)

    for letter in ascii_lowercase[:len(dimensions)]:
        comp = Component(np.random.random(dimensions))
        data.add_component(comp, letter)

    return data


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
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
    layer_state.vmin = 0.1
    layer_state.vmax = 0.9
    layer_state.alpha = 0.8

    layer_state.color = "#ff0000"
    layer_state.cmap = colormaps['Red-Blue']
    layer_state.color_mode = "Fixed"

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
    assert layer_artist.vmin == 0.1
    assert layer_artist.vmax == 0.9
    assert layer_artist.alpha == 0.8

    assert layer_state.color == "#ff0000"
    assert layer_state.cmap == colormaps['Red-Blue']
    assert layer_state.color_mode == "Fixed"

    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_array_shape(tmpdir):
    # Create irregularly shaped data cube
    data = make_test_data((3841, 48, 46))

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data)

    viewer_state = volume.state

    # Get layer artist style editor
    layer_state = viewer_state.layers[0]

    layer_state.attribute = data.id['b']

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_scatter_on_volume(tmpdir):

    data1 = Data(a=np.arange(60).reshape((3, 4, 5)))
    data2 = Data(x=[1, 2, 3], y=[2, 3, 4], z=[3, 4, 5])
    data3 = Data(b=np.arange(60).reshape((3, 4, 5)))

    dc = DataCollection([data1, data2, data3])

    dc.add_link(LinkSame(data1.pixel_component_ids[2], data2.id['x']))
    dc.add_link(LinkSame(data1.pixel_component_ids[1], data2.id['y']))
    dc.add_link(LinkSame(data1.pixel_component_ids[0], data2.id['z']))

    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data1)
    volume.add_data(data2)
    volume.add_data(data3)

    # Check that writing a session works as expected.

    session_file = tmpdir.join('test_scatter_on_volume.glu').strpath
    ga.save_session(session_file)
    ga.close()

    # Now we can check that everything is restored correctly

    ga2 = GlueApplication.restore_session(session_file)
    ga2.show()

    volume_r = ga2.viewers[0][0]

    assert len(volume_r.layers) == 3

    ga2.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_layer_visibility_clip():

    # Regression test for a bug that meant that updating the clip data setting
    # caused a layer to become visible even if it shouldn't be

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data)

    assert volume.layers[0].visible
    assert volume.layers[0]._multivol.enabled[0]

    volume.layers[0].visible = False

    assert not volume.layers[0].visible
    assert not volume.layers[0]._multivol.enabled[0]

    volume.state.clip_data = True

    assert not volume.layers[0].visible
    assert not volume.layers[0]._multivol.enabled[0]

    ga.close()


@pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
def test_remove_subset_group():

    # Regression test for a bug that meant that removing a subset caused an
    # error when multiple viewers were present.

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)
    ga.show()

    volume1 = ga.new_data_viewer(VispyVolumeViewer)
    volume1.add_data(data)

    volume2 = ga.new_data_viewer(VispyVolumeViewer)
    volume2.add_data(data)

    dc.new_subset_group(subset_state=data.id['a'] > 0, label='Subset 1')
    dc.remove_subset_group(dc.subset_groups[0])

    ga.close()


def test_add_data_with_incompatible_subsets(tmpdir):

    data1 = Data(label="Data 1", x=np.arange(24).reshape((4, 3, 2)))
    data2 = Data(label="Data 2", y=np.arange(24).reshape((4, 3, 2)))

    dc = DataCollection([data1, data2])
    ga = GlueApplication(dc)
    ga.show()

    # Subset is defined in terms of data2, so it's an incompatible subset
    # for data1
    dc.new_subset_group(subset_state=data2.id['y'] > 0.5, label='subset 1')

    if IS_WIN:
        pytest.skip(reason='Windows fatal exception: access violation')
    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data1)

    ga.close()


def test_add_higher_dimensional_layers():

    # Check that we can load layers with > 3 dimensions

    shape_4d = (10, 10, 10, 5)
    data_4d = make_test_data(shape_4d)

    shape_5d = (5, 5, 4, 4, 2)
    data_5d = make_test_data(shape_5d)

    dc = DataCollection([data_4d, data_5d])

    ga = GlueApplication(dc)
    ga.show()

    # First add a 4D layer
    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data_4d)

    assert len(volume.layers) == 1

    volume.state.x_att = data_4d.pixel_component_ids[0]
    volume.state.y_att = data_4d.pixel_component_ids[2]
    volume.state.z_att = data_4d.pixel_component_ids[3]

    # Next add a 5D layer
    volume2 = ga.new_data_viewer(VispyVolumeViewer)
    volume2.add_data(data_5d)

    assert len(volume2.layers) == 1

    volume2.state.x_att = data_5d.pixel_component_ids[0]
    volume2.state.y_att = data_5d.pixel_component_ids[4]
    volume2.state.z_att = data_5d.pixel_component_ids[2]

    ga.close()


def test_3d_4d_layers():
    shape_4d = (10, 10, 10, 5)
    data_4d = make_test_data(shape_4d)

    shape_3d = (15, 20, 25)
    data_3d = make_test_data(shape_3d)

    dc = DataCollection([data_4d, data_3d])

    dc.add_link(LinkSame(data_4d.pixel_component_ids[0], data_3d.pixel_component_ids[2]))
    dc.add_link(LinkSame(data_4d.pixel_component_ids[1], data_3d.pixel_component_ids[0]))
    dc.add_link(LinkSame(data_4d.pixel_component_ids[2], data_3d.pixel_component_ids[1]))

    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data_4d)
    volume.add_data(data_3d)
    layer_3d = volume.layers[1]

    volume.state.x_att = data_4d.pixel_component_ids[0]
    volume.state.y_att = data_4d.pixel_component_ids[1]
    volume.state.z_att = data_4d.pixel_component_ids[2]

    assert layer_3d.enabled

    volume.state.y_att = data_4d.pixel_component_ids[3]

    assert not layer_3d.enabled

    ga.close()


def test_scatter_on_4d():
    shape_4d = (10, 10, 10, 5)
    data_4d = make_test_data(shape_4d)

    data_scatter = Data(x=[1, 2, 3], y=[2, 3, 4], z=[3, 4, 5])

    dc = DataCollection([data_4d, data_scatter])

    dc.add_link(LinkSame(data_4d.id['b'], data_scatter.id['x']))
    dc.add_link(LinkSame(data_4d.id['c'], data_scatter.id['y']))
    dc.add_link(LinkSame(data_4d.id['d'], data_scatter.id['z']))

    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data_4d)

    volume.state.x_att = data_4d.pixel_component_ids[1]
    volume.state.y_att = data_4d.pixel_component_ids[2]
    volume.state.z_att = data_4d.pixel_component_ids[3]

    volume.add_data(data_scatter)

    layer_scatter = volume.layers[-1]

    assert layer_scatter.enabled

    volume.state.x_att = data_4d.pixel_component_ids[0]

    assert not layer_scatter.enabled

    volume.state.x_att = data_4d.pixel_component_ids[3]
    volume.state.z_att = data_4d.pixel_component_ids[1]

    assert layer_scatter.enabled

    ga.close()


def test_data_proxy_shape():
    shape_4d = (5, 4, 2, 7)
    data_4d = make_test_data(shape_4d)

    dc = DataCollection([data_4d])

    ga = GlueApplication(dc)
    ga.show()

    volume = ga.new_data_viewer(VispyVolumeViewer)
    volume.add_data(data_4d)
    layer = volume.layers[0]

    volume.state.x_att = data_4d.pixel_component_ids[0]
    volume.state.y_att = data_4d.pixel_component_ids[1]
    volume.state.z_att = data_4d.pixel_component_ids[2]

    proxy = DataProxy(volume.state, layer.state)
    assert proxy.shape == (5, 4, 2)

    volume.state.x_att = data_4d.pixel_component_ids[3]
    assert proxy.shape == (7, 4, 2)

    volume.state.x_att = data_4d.pixel_component_ids[2]
    volume.state.y_att = data_4d.pixel_component_ids[1]
    volume.state.z_att = data_4d.pixel_component_ids[3]
    assert proxy.shape == (2, 4, 7)

    ga.close()
