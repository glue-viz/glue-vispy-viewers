import os
import math

from glue.external.qt import QtGui
from glue.qt.widget_properties import CurrentComboProperty, TextProperty, ButtonProperty
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp

from vispy.color import get_colormaps

__all__ = ["ScatterOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')


class ScatOptionsWidget(QtGui.QWidget):

    def __init__(self, parent=None, vispy_widget=None):

        super(ScatOptionsWidget, self).__init__(parent=parent)

        print('UI_Main', UI_MAIN)
        self.ui = load_ui(UI_MAIN, self)
        if self.ui is None:
            raise Exception("Unable to load UI file: {0}".format(UI_MAIN))

        self._event_lock = False

        self._vispy_widget = vispy_widget
        if vispy_widget is not None:
            self._vispy_widget.options_widget = self

        self._connect()

    # From 2D scatter
    def _connect(self):
        ui = self.ui

        ui.axis_apply.clicked.connect(self._refresh_program)
        ui.reset_button.clicked.connect(self._reset_view)

    def set_valid_components(self, components):
        self.ui.xAxisComboBox.clear()
        self.ui.yAxisComboBox.clear()
        self.ui.zAxisComboBox.clear()
        self.ui.SizeComboBox.clear()
        for component in components:
            self.ui.xAxisComboBox.addItem(component, component)
            self.ui.yAxisComboBox.addItem(component, component)
            self.ui.zAxisComboBox.addItem(component, component)
            self.ui.SizeComboBox.addItem(component, component)

    def _apply(self):
        self._reset_clim()
        self._refresh_program()

    def _reset_view(self):
        # self._reset_clim()
        self._refresh_viewer()

    def _reset_clim(self):
        self.xmin = 'auto'
        self.xmax = 'auto'
        self.ymin = 'auto'
        self.ymax = 'auto'
        self.zmin = 'auto'
        self.zmax = 'auto'

    # TODO: self._vispy_widget._refresh() is empty now
    def _refresh_viewer(self):
        if self._vispy_widget is not None:
            self._vispy_widget._refresh()

    def _refresh_program(self):

        if self._vispy_widget is not None:
            self._vispy_widget.set_program()