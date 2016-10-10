from __future__ import absolute_import, division, print_function

# Import vispy.gloo first when on Windows otherwise there are strange
# side-effects when PyQt4.Qt is imported first (which it now is in QtPy)
import sys
if sys.platform.startswith('win'):
    import glue_vispy_viewers.extern.vispy.gloo.gl

from glue.utils.qt import get_qapp

# The application has to always be referenced to avoid being shut down, so we
# keep a reference to it here
app = None


def pytest_configure(config):
    global app
    app = get_qapp()
