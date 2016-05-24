__author__ = 'penny'


def setup():
    from .scatter_viewer import VispyScatterViewer
    from glue.config import qt_client
    qt_client.add(VispyScatterViewer)
