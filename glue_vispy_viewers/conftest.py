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

from glue.core.fixed_resolution_buffer import PIXEL_CACHE, ARRAY_CACHE


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


def pytest_ignore_collect(collection_path, config):
    if collection_path.is_dir():
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


import pytest as _pytest  # noqa: E402


@_pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):

    # Hookwrapper so xunit setup/teardown methods (setup_method /
    # teardown_method) run BEFORE our checks. Without this, a class-based
    # test that creates a viewer in setup_method and closes it in
    # teardown_method would still appear to be leaking viewers at the time
    # the objgraph check runs.
    yield

    # The following is a check to make sure that once the viewer and
    # application have been closed, there are no leftover references to data
    # viewers or application. This was introduced because there were
    # previously circular references that meant that viewer instances were
    # not properly garbage collected, which in turn meant they still reacted
    # in some cases to events.

    # Make sure pixel and array cache is empty - if it isn't, it usually
    # indicates the viewer has not been closed/cleaned up correctly
    if len(PIXEL_CACHE) > 0:
        raise Exception("Pixel cache contains {0} elements".format(len(PIXEL_CACHE)))
    if len(ARRAY_CACHE) > 0:
        raise Exception("Array cache contains {0} elements".format(len(ARRAY_CACHE)))

    # Temporarily skip this test for test_add_viewer while trying to determine cause
    if item.name == 'test_add_viewer':
        return

    if OBJGRAPH_INSTALLED and hasattr(item, '_viewer_count'):

        if GLUEQT_INSTALLED:
            app.processEvents()

        # A class-based test may still hold references via self even after
        # teardown_method nulls them out, until Python collects the test
        # instance. Force a collection here so the viewer count check sees
        # the post-cleanup state.
        import gc
        gc.collect()

        for viewer_cls in VIEWER_CLASSES:

            obj = objgraph.by_type(viewer_cls)

            if len(obj) > item._viewer_count:
                objgraph.show_backrefs(objgraph.by_type(viewer_cls))
                raise ValueError("No net viewers should be created in tests")
