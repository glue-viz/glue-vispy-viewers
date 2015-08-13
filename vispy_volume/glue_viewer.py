__author__ = 'penny'

from glue.qt.widgets.data_viewer import DataViewer

# Add a __init__.py file to this folder can solve the relative import problem
from .vispy_widget import QtVispyWidget


class GlueVispyViewer(DataViewer):

    LABEL = "3D Volume"

    def __init__(self, session, parent=None):
        super(GlueVispyViewer, self).__init__(session, parent=parent)
        self._vispy_widget = QtVispyWidget()
        self.setCentralWidget(self._vispy_widget.canvas.native)

    def add_data(self, data):
        self._vispy_widget.set_data(data['PRIMARY'])
        self._vispy_widget.set_canvas()
        self._vispy_widget.canvas.render()
        return True
