import numpy as np
from ..scat_vispy_widget import QtScatVispyWidget
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
    comp_mass = glue.core.data.Component(np.array([0.55, 1, 1.5]))

    data.add_component(comp_x1, 'x_gal')
    data.add_component(comp_y1, 'y_gal')
    data.add_component(comp_z1, 'z_gal')
    data.add_component(comp_mass, 'mass')

    return data

def test_widget():

    # Make sure QApplication is started
    get_qapp()

    # Create fake data
    # data = Data(primary=np.arange(1000).reshape((10,10,10)))

    # fits_file_name = '/Users/penny/Works/cloud_catalog_july14_2015.fits'
    # fitsfile = pyfits.open(fits_file_name)

    # Set up widget
    w = QtScatVispyWidget()
    # op = VolumeOptionsWidget(vispy_widget=w)
    w.data = test_categorical_data()
    w.set_program()
    w.set_projection()
    # w.on_draw()
    w.canvas.show()


    # Test timer
    # w.on_timer(TimerEvent(type='timer_timeout', iteration=3))

    # Test key presses
    # w.on_key_press(KeyEvent(text=' '))
    # w.on_key_press(KeyEvent(text=''))
    # w.on_key_press(KeyEvent(text='3'))

    # Test mouse_wheel
    # w.on_mouse_wheel(MouseEvent(type='mouse_wheel', delta=(0, 0.5)))
    # w.on_mouse_wheel(MouseEvent(type='mouse_wheel', delta=(0, -0.3)))

