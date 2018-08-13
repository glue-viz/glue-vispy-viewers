from .version import __version__  # noqa

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'


import ctypes
ctypes.CDLL("libGL.so.1", mode=ctypes.RTLD_GLOBAL)

print("HERE")

#try:
#    import OpenGL  # noqa
#except ImportError:
# #   raise ImportError("The PyOpenGL package is required for this plugin")
#else:
#    del OpenGL
