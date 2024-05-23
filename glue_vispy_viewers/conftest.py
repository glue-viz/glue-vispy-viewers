# Import vispy.gloo first when on Windows otherwise there are strange
# side-effects when PyQt4.Qt is imported first (which it now is in QtPy)
import os
import sys
if sys.platform.startswith('win'):
    import vispy.gloo.gl  # noqa

try:
    import qtpy  # noqa
    from glue_qt.utils import get_qapp  # noqa
except ImportError:
    GLUEQT_INSTALLED = False
else:
    GLUEQT_INSTALLED = True

try:
    import glue_jupyter  # noqa
except ImportError:
    GLUEJUPYTER_INSTALLED = False
else:
    GLUEJUPYTER_INSTALLED = True

try:
    import objgraph
except ImportError:
    OBJGRAPH_INSTALLED = False
else:
    OBJGRAPH_INSTALLED = True

# The application has to always be referenced to avoid being shut down, so we
# keep a reference to it here
if GLUEQT_INSTALLED:
    app = None


def pytest_configure(config):
    os.environ['GLUE_TESTING'] = 'True'
    if GLUEQT_INSTALLED:
        global app
        app = get_qapp()


def pytest_unconfigure(config):
    os.environ.pop('GLUE_TESTING')
    if GLUEQT_INSTALLED:
        global app
        app = None


VIEWER_CLASSES = ['VispyScatterViewer', 'VispyVolumeViewer']


def pytest_ignore_collect(collection_path, path, config):
    if path.isdir():
        if "qt" in collection_path.parts:
            return not GLUEQT_INSTALLED
        if "jupyter" in collection_path.parts:
            return not GLUEJUPYTER_INSTALLED


def pytest_runtest_setup(item):

    if OBJGRAPH_INSTALLED:

        if GLUEQT_INSTALLED:
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

    # Temporarily skip this test for test_add_viewer while trying to determine cause
    if item.name == 'test_add_viewer':
        return

    if OBJGRAPH_INSTALLED and hasattr(item, '_viewer_count'):

        if GLUEQT_INSTALLED:
            app.processEvents()

        for viewer_cls in VIEWER_CLASSES:

            obj = objgraph.by_type(viewer_cls)

            if len(obj) > item._viewer_count:
                objgraph.show_backrefs(objgraph.by_type(viewer_cls))
                raise ValueError("No net viewers should be created in tests")
