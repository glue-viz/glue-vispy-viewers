from .version import __version__  # noqa

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'

try:
    import OpenGL  # noqa
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
else:
    del OpenGL
