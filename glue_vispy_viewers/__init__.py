import importlib.metadata

__version__ = importlib.metadata.version("glue-vispy-viewers")

try:
    import OpenGL  # noqa
except ImportError:
    raise ImportError("The PyOpenGL package is required for this plugin")
else:
    del OpenGL

# Ensure we can read old session files prior to the Qt/Jupyter split
from glue.core.state import PATH_PATCHES

PATH_PATCHES[
    "glue_vispy_viewers.scatter.scatter_viewer.VispyScatterViewer"
] = "glue_vispy_viewers.scatter.qt.scatter_viewer.VispyScatterViewer"
PATH_PATCHES[
    "glue_vispy_viewers.volume.volume_viewer.VispyVolumeViewer"
] = "glue_vispy_viewers.volume.qt.volume_viewer.VispyVolumeViewer"
del PATH_PATCHES
