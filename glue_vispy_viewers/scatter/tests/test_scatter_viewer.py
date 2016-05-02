import numpy as np

from glue.core import DataCollection, Data
from glue.app.qt.application import GlueApplication
from glue.core.component import Component

from matplotlib import cm

from ..scatter_viewer import VispyScatterViewer

def make_test_data():

    data = Data(label="Test Cat Data 1")

    np.random.seed(12345)

    for letter in 'abcdefxyz':
        comp = Component(np.random.random(100))
        data.add_component(comp, letter)

    return data

def test_scatter_viewer():

    # Create fake data
    data = make_test_data()

    # Create fake session

    dc = DataCollection([data])
    ga = GlueApplication(dc)

    w = ga.new_data_viewer(VispyScatterViewer)
    w.add_data(data)

    options = w.options_widget()

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

    # Get layer artist style editor
    layer_artist = list(w._view.layout_style_widgets.keys())[0]
    style_widget = w._view.layout_style_widgets[layer_artist]

    style_widget._set_size_mode('linear')
    style_widget.size_attribute = data.id['c']
    style_widget.size_scaling = 2
    style_widget.size_vmin = 0.2
    style_widget.size_vmax = 0.8

    style_widget._set_color_mode('linear')
    style_widget.cmap_attribute = data.id['y']
    style_widget.cmap_vmin = 0.1
    style_widget.cmap_vmax = 0.9
    style_widget.cmap = cm.BuGn
