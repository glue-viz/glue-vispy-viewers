import os

from qtpy import QtWidgets

from echo.qt import autoconnect_callbacks_to_qt

from glue_qt.utils import load_ui

__all__ = ["VispyOptionsWidget"]


class VispyOptionsWidget(QtWidgets.QWidget):

    def __init__(self, viewer_state=None, session=None, parent=None):

        super(VispyOptionsWidget, self).__init__(parent=parent)

        self._data_collection = session.data_collection

        self.ui = load_ui('viewer_options.ui', self,
                          directory=os.path.dirname(__file__))

        connect_kwargs = {'value_x_stretch': dict(value_range=(0.1, 10), log=True),
                          'value_y_stretch': dict(value_range=(0.1, 10), log=True),
                          'value_z_stretch': dict(value_range=(0.1, 10), log=True),
                          'valuetext_x_stretch': dict(fmt='{:6.2f}'),
                          'valuetext_y_stretch': dict(fmt='{:6.2f}'),
                          'valuetext_z_stretch': dict(fmt='{:6.2f}')}

        if not hasattr(viewer_state, 'downsample'):
            self.ui.bool_downsample.hide()

        if not hasattr(viewer_state, 'resolution'):
            self.ui.label_resolution.hide()
            self.ui.combosel_resolution.hide()

        if not hasattr(viewer_state, 'reference_data'):
            self.ui.label_reference_data.hide()
            self.ui.combosel_reference_data.hide()

        self.ui.label_line_width.hide()
        self.ui.value_line_width.hide()

        self._connections = autoconnect_callbacks_to_qt(viewer_state, self.ui, connect_kwargs)
