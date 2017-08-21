import os

from qtpy import QtWidgets

from glue.external.echo.qt import autoconnect_callbacks_to_qt

from glue.utils.qt import load_ui

__all__ = ["VispyOptionsWidget"]


class VispyOptionsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, viewer_state=None):

        super(VispyOptionsWidget, self).__init__(parent=parent)

        self._data_collection = self.parent()._data

        self.ui = load_ui('viewer_options.ui', self,
                          directory=os.path.dirname(__file__))

        connect_kwargs = {'value_x_stretch': dict(value_range=(0.1, 10), log=True),
                          'value_y_stretch': dict(value_range=(0.1, 10), log=True),
                          'value_z_stretch': dict(value_range=(0.1, 10), log=True),
                          'valuetext_x_stretch': dict(fmt='{:6.2f}'),
                          'valuetext_y_stretch': dict(fmt='{:6.2f}'),
                          'valuetext_z_stretch': dict(fmt='{:6.2f}')}

        autoconnect_callbacks_to_qt(viewer_state, self.ui, connect_kwargs)
