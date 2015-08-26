from glue.qt import get_qapp
from ..glue_viewer import GlueVispyViewer
from glue.config import qt_client

def test_viewer():

    # Make sure QApplication is started
    get_qapp()

    # v = GlueVispyViewer()

    qt_client.add(GlueVispyViewer)