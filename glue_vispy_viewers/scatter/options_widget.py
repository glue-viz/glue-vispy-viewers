import os
import math

from glue.external.qt import QtGui, QtCore
from glue.qt.widget_properties import CurrentComboProperty, TextProperty, ValueProperty
from glue.qt.qtutil import load_ui
from glue.qt import get_qapp

from vispy.color import get_colormaps, get_color_dict, get_color_names

__all__ = ["ScatterOptionsWidget"]

UI_MAIN = os.path.join(os.path.dirname(__file__), 'options_widget.ui')


class ScatOptionsWidget(QtGui.QWidget):

    cmin = TextProperty('ui.clim_min')
    cmax = TextProperty('ui.clim_max')

    color = CurrentComboProperty('ui.ColorComboBox')
    opacity = ValueProperty('ui.OpacitySlider')

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

        # There are 155 color options
        for map_name in get_color_names():
            self.ui.ColorComboBox.addItem(map_name, map_name)

        # Add a color display area here
        # self.opacity = self.ui.opacity.value()
        self.color_view = self.ui.graphicsView
        self.color_scene = QtGui.QGraphicsScene()
        self.color_view.setBackgroundBrush(QtGui.QColor(self.color))
        self.color_view.setScene(self.color_scene)
        self.color_view.show()

        self._connect()

    # From 2D scatter
    def _connect(self):
        ui = self.ui

        ui.axis_apply.clicked.connect(self._apply)
        ui.reset_button.clicked.connect(self._apply)
        ui.ClimComboBox.currentIndexChanged.connect(self._clim_change)
        ui.ColorComboBox.currentIndexChanged.connect(self._color_changed)
        ui.OpacitySlider.valueChanged.connect(self._refresh_program)

        ui.clim_min.returnPressed.connect(self._draw_clim)
        ui.clim_max.returnPressed.connect(self._draw_clim)

    def set_valid_components(self, components):
        self.ui.xAxisComboBox.clear()
        self.ui.yAxisComboBox.clear()
        self.ui.zAxisComboBox.clear()
        self.ui.SizeComboBox.clear()
        self.ui.ClimComboBox.clear()
        for component in components:
            self.ui.xAxisComboBox.addItem(component, component)
            self.ui.yAxisComboBox.addItem(component, component)
            self.ui.zAxisComboBox.addItem(component, component)
            self.ui.SizeComboBox.addItem(component, component)
            self.ui.ClimComboBox.addItem(component, component)

    def _clim_change(self):
        if self._vispy_widget is not None:
            self._vispy_widget._update_clim()

    def _draw_clim(self):
        # Pick the dataset between the threshold and draw them in different symbol
        # Add another visual into it?
        if self._vispy_widget is not None:
            self._vispy_widget.apply_clim()

    def _apply(self):
        self._reset_clim()
        self._refresh_program()

    def _reset_view(self):
        # self._reset_clim()
        self._refresh_viewer()

    def _reset_clim(self):
        self.cmin = 'auto'
        self.cmax = 'auto'

    def _color_changed(self):
        self.color_view.setScene(self.color_scene)
        self.color_view.setBackgroundBrush(QtGui.QColor(self.color))
        self.color_view.show()

        # self._refresh_program()

    # TODO: self._vispy_widget._refresh() is empty now
    def _refresh_viewer(self):
        if self._vispy_widget is not None:
            self._vispy_widget._refresh()

    def _refresh_program(self):

        if self._vispy_widget is not None:
            self._vispy_widget.set_program()