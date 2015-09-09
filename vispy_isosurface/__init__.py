__author__ = 'penny'

def setup():
    from .isosurface_viewer import GlueVispyIsosurfaceViewer
    from glue.config import qt_client
    qt_client.add(GlueVispyIsosurfaceViewer)