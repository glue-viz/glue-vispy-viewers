def setup():
    from .isosurface_viewer import VispyIsosurfaceViewer
    from glue.config import qt_client
    qt_client.add(VispyIsosurfaceViewer)
