__author__ = 'penny'


def setup():
    from .volume_viewer import VispyVolumeViewer
    from glue.config import qt_client
    qt_client.add(VispyVolumeViewer)
