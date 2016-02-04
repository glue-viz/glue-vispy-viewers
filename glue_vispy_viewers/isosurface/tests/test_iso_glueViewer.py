from glue.external.qt import get_qapp
from ..iso_glue_viewer import GlueIsoVispyViewer
from glue.config import qt_client

def test_viewer():

    # Make sure QApplication is started
    get_qapp()

    # v = GlueVispyViewer()

    qt_client.add(GlueIsoVispyViewer)