from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = 'undefined'

try:
    import OpenGL  # noqa
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
else:
    del OpenGL
