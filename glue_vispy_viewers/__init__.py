import importlib.metadata

__version__ = importlib.metadata.version('glue-vispy-viewers')

try:
    import OpenGL  # noqa
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
else:
    del OpenGL
