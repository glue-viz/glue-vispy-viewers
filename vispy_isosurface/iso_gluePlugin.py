__author__ = 'penny'

def setup():
    from .iso_glueViewer import GlueIsoVispyViewer
    from glue.config import qt_client
    qt_client.add(GlueIsoVispyViewer)