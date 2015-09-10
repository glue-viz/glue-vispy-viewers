__author__ = 'penny'

def setup():
    from .vol_glueViewer import GlueVispyViewer
    from glue.config import qt_client
    qt_client.add(GlueVispyViewer)