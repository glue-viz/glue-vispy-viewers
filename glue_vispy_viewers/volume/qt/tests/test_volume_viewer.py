import sys
import pytest
import numpy as np

from glue.core import DataCollection, Data
from glue_qt.app.application import GlueApplication
from glue.core.component import Component
from glue.core.link_helpers import LinkSame
from glue.core.fixed_resolution_buffer import PIXEL_CACHE, ARRAY_CACHE

from ..volume_viewer import VispyVolumeViewer

IS_WIN = sys.platform == 'win32'


def teardown_function(function):
    # Make sure cache is empty
    if len(PIXEL_CACHE) > 0:
        raise Exception("Pixel cache contains {0} elements".format(len(PIXEL_CACHE)))
    if len(ARRAY_CACHE) > 0:
        raise Exception("Array cache contains {0} elements".format(len(ARRAY_CACHE)))


def make_test_data(dimensions=(10, 10, 10)):

    data = Data(label="Test Cube Data")

    np.random.seed(12345)

    for letter in 'abc':
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
