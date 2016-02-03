import numpy as np
from ..scat_vispy_widget import QtScatVispyWidget
from ..options_widget import ScatOptionsWidget
from glue.qt import get_qapp
# import pyfits
import glue

class KeyEvent(object):
    def __init__(self, text):
        self.text = text

class MouseEvent(object):
    def __init__(self, delta, type):
        self.type = type
        self.delta = delta

class TimerEvent(object):
    def __init__(self, type, iteration):
        self.type = type
        self.iteration = iteration

def test_categorical_data():

    data = glue.core.data.Data(label="Test Cat Data 1")

    comp_x1 = glue.core.data.Component(np.array([4, 5, 6]))
    comp_y1 = glue.core.data.Component(np.array([1, 2, 3]))
    comp_z1 = glue.core.data.Component(np.array([2, 3, 4]))
    comp_size = glue.core.data.Component(np.array([1.0, 1.0, 1.0]))
    # Use the comp_x1 as the clim object
    comp_clim = glue.core.data.Component(np.array([4, 5, 6]))

    data.add_component(comp_x1, 'x_gal')
    data.add_component(comp_y1, 'y_gal')
    data.add_component(comp_z1, 'z_gal')
    data.add_component(comp_size, 'size')
    data.add_component(comp_clim, 'clim')

    return data

def test_widget():

    # Make sure QApplication is started
    get_qapp()

    # Set up widget
    w = QtScatVispyWidget()
    op = ScatOptionsWidget(vispy_widget=w)
    w.data = test_categorical_data()
    w.add_scatter_visual()
    w.canvas.show()

