from glue.qt import get_qapp
from ..scat_vispy_viewer import ScatVispyViewer
from glue.config import qt_client

def test_viewer():

    # Make sure QApplication is started
    get_qapp()

    # v = GlueVispyViewer()
    # v = GlueVispyViewer()

    qt_client.add(ScatVispyViewer)
