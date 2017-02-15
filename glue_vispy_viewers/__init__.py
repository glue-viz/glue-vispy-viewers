from .version import __version__  # noqa

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'

try:
    import OpenGL  # noqa
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
else:
    del OpenGL

import sys
from qtpy import PYQT5
BROKEN_PYQT5 = (PYQT5 and sys.platform == 'linux' and
                'Continuum Analytics' in sys.version)
del sys, PYQT5
