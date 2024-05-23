# Make sure that session files can be read in a backward-compatible manner

import os
import pytest
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_equal

from glue.core.state import GlueUnSerializer

from qtpy.QtWidgets import QMessageBox

DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.mark.parametrize('protocol', [0, 1])
def test_scatter_volume(protocol):

    filename = os.path.join(DATA, 'scatter_volume_v{0}.glu'.format(protocol))

    with open(filename, 'r') as f:
        session = f.read()

    with patch.object(QMessageBox, 'question') as question:
        question.return_value = QMessageBox.Yes
        state = GlueUnSerializer.loads(session)
        ga = state.object('__main__')

    dc = ga.session.data_collection

    assert len(dc) == 2

    assert dc[0].label == 'table'
    assert dc[1].label == 'array'

    # SCATTER VIEWER

    scatter = ga.viewers[0][0]

    viewer_state = scatter.state

    assert viewer_state.x_att.label == 'b'
    assert viewer_state.x_min == 8
    assert viewer_state.x_max == 0
    np.testing.assert_allclose(viewer_state.x_stretch, 0.4, rtol=1.e-3)

    assert viewer_state.y_att.label == 'a'
    assert viewer_state.y_min == 0.4
    assert viewer_state.y_max == 4
    np.testing.assert_allclose(viewer_state.y_stretch, 0.6, rtol=1.e-3)

    assert viewer_state.z_att.label == 'c'
    assert viewer_state.z_min == 2
    assert viewer_state.z_max == 5.4
    np.testing.assert_allclose(viewer_state.z_stretch, 1.4, rtol=1.e-3)

    assert viewer_state.perspective_view
    assert not viewer_state.visible_axes
    if protocol >= 1:
        assert not viewer_state.native_aspect
        assert viewer_state.clip_data

    layer_state = viewer_state.layers[0]

    assert layer_state.size_mode == 'Linear'
    assert layer_state.size_attribute.label == 'e'
    assert layer_state.size_vmin == 3
    assert layer_state.size_vmax == 4
    np.testing.assert_allclose(layer_state.size_scaling, 1.51356, rtol=1.e-3)

    assert layer_state.color_mode == 'Linear'
    assert layer_state.cmap_attribute.label == 'd'
    assert layer_state.cmap_vmin == 0
    assert layer_state.cmap_vmax == 10
    assert layer_state.alpha == 0.66

    # VOLUME VIEWER

    volume = ga.viewers[0][1]

    viewer_state = volume.state

    assert viewer_state.x_att.label == 'Pixel Axis 2 [x]'
    assert viewer_state.x_min == 3.5
    assert viewer_state.x_max == -0.5
    np.testing.assert_allclose(viewer_state.x_stretch, 0.2, rtol=1.e-3)

    assert viewer_state.y_att.label == 'Pixel Axis 1 [y]'
    assert viewer_state.y_min == -0.5
    assert viewer_state.y_max == 2.5
    np.testing.assert_allclose(viewer_state.y_stretch, 1.2, rtol=1.e-3)

    assert viewer_state.z_att.label == 'Pixel Axis 0 [z]'
    assert viewer_state.z_min == -0.5
    assert viewer_state.z_max == 1.5
    np.testing.assert_allclose(viewer_state.z_stretch, 1.3, rtol=1.e-3)

    assert not viewer_state.perspective_view
    assert viewer_state.visible_axes
    if protocol >= 1:
        assert viewer_state.native_aspect
        assert not viewer_state.clip_data

    layer_state = viewer_state.layers[0]

    assert layer_state.attribute == 'array'
    assert layer_state.vmin == 0
    assert layer_state.vmax == 23
    assert layer_state.color == '#e60010'
    assert layer_state.alpha == 0.36

    ga.close()


def test_scatter_volume_selection():

    filename = os.path.join(DATA, 'scatter_volume_selection.glu')

    with open(filename, 'r') as f:
        session = f.read()

    with patch.object(QMessageBox, 'question') as question:
        question.return_value = QMessageBox.Yes
        state = GlueUnSerializer.loads(session)
        ga = state.object('__main__')

    dc = ga.session.data_collection

    assert len(dc) == 2

    assert dc[0].label == 'array'
    assert dc[1].label == 'table'

    expected_array = np.array([[[0, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0]],
                               [[0, 0, 0, 0],
                                [0, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 1, 1, 1]],
                               [[0, 0, 0, 0],
                                [0, 0, 1, 1],
                                [0, 1, 1, 1],
                                [0, 1, 1, 1]],
                               [[0, 0, 1, 1],
                                [0, 0, 1, 1],
                                [0, 1, 1, 1],
                                [0, 0, 0, 1]]], dtype=bool)

    expected_table = np.array([0, 1, 0], dtype=bool)

    assert_equal(dc[0].subsets[0].to_mask(), expected_array)
    assert_equal(dc[1].subsets[0].to_mask(), expected_table)

    ga.close()


@pytest.mark.parametrize('protocol', [1, 2])
def test_multiple_volumes(protocol):

    # Before glue-vispy-viewers 0.12, volumes could be shown together without
    # being linked, so when loading old session files we should suggest to
    # auto link.

    filename = os.path.join(DATA, 'multiple_volumes_v{0}.glu'.format(protocol))

    with open(filename, 'r') as f:
        session = f.read()

    with patch.object(QMessageBox, 'question') as question:
        question.return_value = QMessageBox.Yes
        state = GlueUnSerializer.loads(session)
        ga = state.object('__main__')

    volume = ga.viewers[0][0]

    assert volume.layers[0].enabled
    assert volume.layers[1].enabled
    assert volume.layers[2].enabled
    assert volume.layers[3].enabled
    assert volume.layers[4].enabled
    assert volume.layers[5].enabled

    ga.close()
