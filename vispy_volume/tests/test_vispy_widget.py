import numpy as np
from ..vol_vispy_widget import QtVispyWidget
from ..options_widget import VolumeOptionsWidget
from glue.qt import get_qapp


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

def test_widget():

    # Make sure QApplication is started
    get_qapp()

    # Create fake data
    data = np.arange(1000).reshape((10,10,10))

    # Set up widget
    w = QtVispyWidget()
    w.set_data(data)
    w.add_volume_visual()
    w.canvas.render()

    # Test timer
    w.on_timer(TimerEvent(type='timer_timeout', iteration=3))

    # Test key presses
    # w.on_key_press(KeyEvent(text='1'))
    # w.on_key_press(KeyEvent(text='2'))
    # w.on_key_press(KeyEvent(text='3'))

    # Test mouse_wheel
    w.on_mouse_wheel(MouseEvent(type='mouse_wheel', delta=(0, 0.5)))
    w.on_mouse_wheel(MouseEvent(type='mouse_wheel', delta=(0, -0.3)))

    op = VolumeOptionsWidget(vispy_widget=w)
    op.update_viewer()