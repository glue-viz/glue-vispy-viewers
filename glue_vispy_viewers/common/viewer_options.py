import os
import math
from functools import partial

from glue.external.qt import QtGui

from glue.utils.qt.widget_properties import CurrentComboProperty, FloatLineProperty
from glue.utils.qt import load_ui

__all__ = ["VispyOptionsWidget"]


class VispyOptionsWidget(QtGui.QWidget):

    x_att = CurrentComboProperty('ui.combo_x_attribute')
    x_min = FloatLineProperty('ui.value_x_min')
    x_max = FloatLineProperty('ui.value_x_max')
    x_stretch = FloatLineProperty('ui.value_x_stretch')

    y_att = CurrentComboProperty('ui.combo_y_attribute')
    y_min = FloatLineProperty('ui.value_y_min')
    y_max = FloatLineProperty('ui.value_y_max')
    y_stretch = FloatLineProperty('ui.value_y_stretch')

    z_att = CurrentComboProperty('ui.combo_z_attribute')
    z_min = FloatLineProperty('ui.value_z_min')
    z_max = FloatLineProperty('ui.value_z_max')
    z_stretch = FloatLineProperty('ui.value_z_stretch')

    def __init__(self, parent=None, vispy_widget=None, data_viewer=None):

        super(VispyOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui('viewer_options.ui', self,
                          directory=os.path.dirname(__file__))

        self._vispy_widget = vispy_widget
        vispy_widget.options = self
        self._data_viewer = data_viewer

        self.stretch_sliders = [self.ui.slider_x_stretch,
                                self.ui.slider_y_stretch,
                                self.ui.slider_z_stretch]

        self.stretch_values = [self.ui.value_x_stretch,
                               self.ui.value_y_stretch,
                               self.ui.value_z_stretch]

        self._event_lock = False

        for slider, label in zip(self.stretch_sliders, self.stretch_values):
            slider.valueChanged.connect(partial(self._update_labels_from_sliders, label, slider))
            label.returnPressed.connect(partial(self._update_sliders_from_labels, slider, label))
            label.setText('1.0')
            label.returnPressed.emit()
            slider.valueChanged.connect(self._update_stretch)

        self.ui.combo_x_attribute.currentIndexChanged.connect(self._data_viewer._update_attributes)
        self.ui.combo_y_attribute.currentIndexChanged.connect(self._data_viewer._update_attributes)
        self.ui.combo_z_attribute.currentIndexChanged.connect(self._data_viewer._update_attributes)

        self.ui.value_x_min.returnPressed.connect(self._vispy_widget._update_limits)
        self.ui.value_y_min.returnPressed.connect(self._vispy_widget._update_limits)
        self.ui.value_z_min.returnPressed.connect(self._vispy_widget._update_limits)

        self.ui.value_x_max.returnPressed.connect(self._vispy_widget._update_limits)
        self.ui.value_y_max.returnPressed.connect(self._vispy_widget._update_limits)
        self.ui.value_z_max.returnPressed.connect(self._vispy_widget._update_limits)

        self.ui.reset_button.clicked.connect(self._vispy_widget._reset_view)

        self._set_attributes_enabled(False)
        self._set_limits_enabled(False)

        self._first_attributes = True

    def set_limits(self, x_min, x_max, y_min, y_max, z_min, z_max):

        self._set_limits_enabled(False)

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

        self._set_limits_enabled(True)

        self.ui.value_x_min.returnPressed.emit()

    def _set_attributes_enabled(self, value):

        self.ui.combo_x_attribute.setEnabled(value)
        self.ui.combo_y_attribute.setEnabled(value)
        self.ui.combo_z_attribute.setEnabled(value)

    def _set_limits_enabled(self, value):

        self.ui.value_x_min.setEnabled(value)
        self.ui.value_y_min.setEnabled(value)
        self.ui.value_z_min.setEnabled(value)

        self.ui.value_x_max.setEnabled(value)
        self.ui.value_y_max.setEnabled(value)
        self.ui.value_z_max.setEnabled(value)

    def _update_attributes(self, components):

        for component in components:
            if self.ui.combo_x_attribute.findData(component) == -1:
                self.ui.combo_x_attribute.addItem(component.label, userData=component)
            if self.ui.combo_y_attribute.findData(component) == -1:
                self.ui.combo_y_attribute.addItem(component.label, userData=component)
            if self.ui.combo_z_attribute.findData(component) == -1:
                self.ui.combo_z_attribute.addItem(component.label, userData=component)

        if self._first_attributes:
            n_max = len(components)
            self.ui.combo_x_attribute.setCurrentIndex(0)
            self.ui.combo_y_attribute.setCurrentIndex(min(1, n_max-1))
            self.ui.combo_z_attribute.setCurrentIndex(min(2, n_max-1))
            self._set_attributes_enabled(True)
            self._first_attributes = False

    def _update_stretch(self):
        self._vispy_widget._update_stretch(self.x_stretch,
                                           self.y_stretch,
                                           self.z_stretch)

    def _update_labels_from_sliders(self, label, slider):
        if self._event_lock:
            return  # prevent infinite event loop
        self._event_lock = True
        try:
            label.setText("{0:6.2f}".format(10** (slider.value() / 1e4)))
        finally:
            self._event_lock = False

    def _update_sliders_from_labels(self, slider, label):
        if self._event_lock:
            return  # prevent infinite event loop
        self._event_lock = True
        try:
            slider.setValue(1e4 * math.log10(float(label.text())))
        finally:
            self._event_lock = False
