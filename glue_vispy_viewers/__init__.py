from .version import __version__

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'

try:
    import OpenGL
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
