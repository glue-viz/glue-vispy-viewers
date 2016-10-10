from .version import __version__

BACKGROUND_COLOR = 'black'
FOREGROUND_COLOR = 'white'

try:
    import OpenGL
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")

from distutils.version import LooseVersion
from glue import __version__ as __glue_version__
if LooseVersion(__glue_version__) < LooseVersion('0.9.0'):
    raise ValueError("Glue 0.9 or later is required for this version of the plugin")
else:
    del LooseVersion
    del __glue_version__
