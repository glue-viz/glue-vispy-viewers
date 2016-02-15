from glue.external.qt import get_qapp
from ..scat_vispy_viewer import VispyScatterViewer
from glue.config import qt_client

def test_viewer():

    # v = GlueVispyViewer()
    # v = GlueVispyViewer()

    qt_client.add(VispyScatterViewer)
