# Import vispy.gloo first when on Windows otherwise there are strange
# side-effects when PyQt4.Qt is imported first (which it now is in QtPy)
import os
import sys
if sys.platform.startswith('win'):
    import vispy.gloo.gl  # noqa

from glue.utils.qt import get_qapp  # noqa

try:
    import objgraph
except ImportError:
    OBJGRAPH_INSTALLED = False
else:
    OBJGRAPH_INSTALLED = True

# The application has to always be referenced to avoid being shut down, so we
# keep a reference to it here
app = None


def pytest_configure(config):
    os.environ['GLUE_TESTING'] = 'True'
    global app
    app = get_qapp()


def pytest_unconfigure(config):
    os.environ.pop('GLUE_TESTING')
    global app
    app = None


VIEWER_CLASSES = ['VispyScatterViewer', 'VispyIsosurfaceViewer', 'VispyVolumeViewer']


def pytest_runtest_setup(item):

    if OBJGRAPH_INSTALLED:

        app.processEvents()

        for viewer_cls in VIEWER_CLASSES:

            obj = objgraph.by_type(viewer_cls)

            item._viewer_count = len(obj)


def pytest_runtest_teardown(item, nextitem):

    # The following is a check to make sure that once the viewer and
    # application have been closed, there are no leftover references to data
    # viewers or application. This was introduced because there were
    # previously circular references that meant that viewer instances were
    # not properly garbage collected, which in turn meant they still reacted
    # in some cases to events.

    if OBJGRAPH_INSTALLED and hasattr(item, '_viewer_count'):

        app.processEvents()

        for viewer_cls in VIEWER_CLASSES:

            obj = objgraph.by_type(viewer_cls)

            if len(obj) > item._viewer_count:
                objgraph.show_backrefs(objgraph.by_type(viewer_cls))
                raise ValueError("No net viewers should be created in tests")
