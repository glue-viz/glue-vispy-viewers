import numpy as np

from glue.external.qt import get_qapp

from glue.core.data import Data
from glue.core.component import Component
from glue.core.tests.util import simple_session

from ..scatter_viewer import VispyScatterViewer

def make_test_data():

    data = Data(label="Test Cat Data 1")

    comp_x1 = Component(np.array([4, 5, 6, 3]))
    comp_y1 = Component(np.array([1, 2, 3, 2]))
    comp_z1 = Component(np.array([2, 3, 4, 1]))

    data.add_component(comp_x1, 'x_gal')
    data.add_component(comp_y1, 'y_gal')
    data.add_component(comp_z1, 'z_gal')

    return data

def test_scatter_viewer():

    # Create fake data
    data = make_test_data()

    # Create fake session
    session = simple_session()
    session.data_collection.append(data)

    w = VispyScatterViewer(session)
    w.add_data(data)
    w.show()
    w._options_widget.show()

    # Get layer artist style editor
    layer_artist, style_widget = w._view.layout_style_widgets.popitem()

    # TODO: add tests when changing the visual properties

