from __future__ import absolute_import, division, print_function

# Import vispy.gloo first when on Windows otherwise there are strange
# side-effects when PyQt4.Qt is imported first (which it now is in QtPy)
import os
import sys
if sys.platform.startswith('win'):
    import glue_vispy_viewers.extern.vispy.gloo.gl  # noqa

qapp = None


def get_qapp(icon_path=None):

    import platform
    from qtpy import QtWidgets, QtGui, QtCore

    global qapp

    qapp = QtWidgets.QApplication.instance()

    if qapp is None:

        # Some Qt modules are picky in terms of being imported before the
        # application is set up, so we import them here.
        # from qtpy import QtWebEngineWidgets  # noqa

        qapp = QtWidgets.QApplication([''])
        qapp.setQuitOnLastWindowClosed(True)

        if icon_path is not None:
            qapp.setWindowIcon(QtGui.QIcon(icon_path))

        if platform.system() == 'Darwin':
            # On Mac, the fonts are generally too large compared to other
            # applications, so we reduce the default here. In future we should
            # make this a setting in the system preferences.
            size_offset = 2
        else:
            # On other platforms, we reduce the font size by 1 point to save
            # space too. Again, this should probably be a global setting.
            size_offset = 1

        font = qapp.font()
        font.setPointSize(font.pointSize() - size_offset)
        qapp.setFont(font)

    # Make sure we use high resolution icons for HDPI displays.
    qapp.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    return qapp

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


def pytest_runtest_teardown(item, nextitem):

    # The following is a check to make sure that once the viewer and
    # application have been closed, there are no leftover references to data
    # viewers or application. This was introduced because there were
    # previously circular references that meant that viewer instances were
    # not properly garbage collected, which in turn meant they still reacted
    # in some cases to events.

    if OBJGRAPH_INSTALLED:

        app.processEvents()

        for viewer_cls in VIEWER_CLASSES:

            obj = objgraph.by_type(viewer_cls)

            if len(obj) > 0:
                objgraph.show_backrefs(objgraph.by_type(viewer_cls))
                raise ValueError("No net viewers should be created in tests")
