__author__ = 'penny'


def setup():
    from .scat_vispy_viewer import ScatVispyViewer
    from glue.config import qt_client
    qt_client.add(ScatVispyViewer)