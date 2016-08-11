# Import vispy.gloo first when on Windows otherwise there are strange
# side-effects when PyQt4.Qt is imported first (which it now is in QtPy)
import sys
if sys.platform.startswith('win'):
    import glue_vispy_viewers.extern.vispy.gloo.gl

from .version import __version__

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'

try:
    import OpenGL
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
