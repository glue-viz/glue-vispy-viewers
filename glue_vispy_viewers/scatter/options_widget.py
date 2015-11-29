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

    # AttributeError: 'ScatOptionsWidget' object has no attribute 'ui'
    '''xlog = ButtonProperty('ui.xLogCheckBox', 'log scaling on x axis?')
    ylog = ButtonProperty('ui.yLogCheckBox', 'log scaling on y axis?')
    zlog = ButtonProperty('ui.zLogCheckBox', 'log scaling on z axis?')

    xflip = ButtonProperty('ui.xFlipCheckBox', 'invert the x axis?')
    yflip = ButtonProperty('ui.yFlipCheckBox', 'invert the y axis?')
    zflip = ButtonProperty('ui.zFlipCheckBox', 'invert the z axis?')

    xmin = TextProperty('ui.xmin', 'Lower x limit of plot')
    xmax = TextProperty('ui.xmax', 'Upper x limit of plot')
    ymin = TextProperty('ui.ymin', 'Lower y limit of plot')
    ymax = TextProperty('ui.ymax', 'Upper y limit of plot')
    zmin = TextProperty('ui.zmin', 'Lower z limit of plot')
    zmax = TextProperty('ui.zmax', 'Upper z limit of plot')

    hidden = ButtonProperty('ui.hidden_attributes', 'Show hidden attributes')'''


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

        self.xatt = CurrentComboProperty('ui.xAxisComboBox')
        self.yatt = CurrentComboProperty('ui.yAxisComboBox')
        self.zatt = CurrentComboProperty('ui.zAxisComboBox')
        self._connect()

    # From 2D scatter
    def _connect(self):
        ui = self.ui

        ui.xAxisComboBox.currentIndexChanged.connect(self._refresh_viewer)
        ui.yAxisComboBox.currentIndexChanged.connect(self._refresh_viewer)
        ui.zAxisComboBox.currentIndexChanged.connect(self._refresh_viewer)

        ui.xmin.returnPressed.connect(self._refresh_viewer)
        ui.xmax.returnPressed.connect(self._refresh_viewer)
        ui.ymin.returnPressed.connect(self._refresh_viewer)
        ui.ymax.returnPressed.connect(self._refresh_viewer)
        ui.zmin.returnPressed.connect(self._refresh_viewer)
        ui.zmax.returnPressed.connect(self._refresh_viewer)

        ui.axis_apply.clicked.connect(self._refresh_program)
        ui.reset_button.clicked.connect(self._reset_view)

    # TODO: implement it
    def set_valid_components(self, components):
        self.ui.xAxisComboBox.clear()
        self.ui.yAxisComboBox.clear()
        self.ui.zAxisComboBox.clear()
        for component in components:
            self.ui.xAxisComboBox.addItem(component, component)
            self.ui.yAxisComboBox.addItem(component, component)
            self.ui.zAxisComboBox.addItem(component, component)

    # Now just for reset clim
    def _reset_view(self):
        self._reset_clim()
        self._refresh_viewer()

    def _reset_clim(self):
        self.xmin = 'auto'
        self.xmax = 'auto'
        self.ymin = 'auto'
        self.ymax = 'auto'
        self.zmin = 'auto'
        self.zmax = 'auto'

    def _refresh_viewer(self):
        if self._vispy_widget is not None:
            self._vispy_widget._refresh()

    def _refresh_program(self):
        if self._vispy_widget is not None:
            self._vispy_widget.set_program()