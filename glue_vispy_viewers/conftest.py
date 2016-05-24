from __future__ import absolute_import, division, print_function

from glue.external.qt import get_qapp

# The application has to always be referenced to avoid being shut down, so we
# keep a reference to it here
app = None


def pytest_configure(config):
    global app
    app = get_qapp()
