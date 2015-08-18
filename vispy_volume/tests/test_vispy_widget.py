# Solve the relative import problem
if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from vispy_widget import QtVispyWidget
    else:
        from ..vispy_widget import QtVispyWidget

import numpy as np
import pyfits
from ..vispy_widget import QtVispyWidget
from glue.qt import get_qapp

class Event(object):
    def __init__(self, text):
        self.text = text


def test_widget():

    fitsdata = pyfits.open('./l1448_13co.fits')
    naxis = fitsdata[0].header['NAXIS']
    image = fitsdata[0].data
    print naxis
    if naxis < 3:
        print 'The data should not be less than 3 dimensions !'
        quit
    elif naxis > 3:
        image = fitsdata[0].data[0,:,:,:]
    print image.shape
    # Set all nan to zero for display
    data = np.nan_to_num(np.array(image))

    # Make sure QApplication is started
    get_qapp()

    assert data is not None
    # Create fake data
    # data = np.arange(1000).reshape((10,10,10))

    # Set up widget
    w = QtVispyWidget()
    w.set_data(data)
    w.set_canvas()
    w.canvas.render()
    w.canvas.show()

    # Test changing colormap
    w.set_colormap()

    # Test key presses
    w.on_key_press(Event(text='1'))
    w.on_key_press(Event(text='2'))
    w.on_key_press(Event(text='3'))

