from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset
from glue.external.qt import QtGui

from glue.utils.qt import load_ui, update_combobox, connect_color
from glue.utils.qt.widget_properties import (ValueProperty,
                                             CurrentComboProperty,
                                             CurrentComboTextProperty,
                                             FloatLineProperty,
                                             connect_float_edit,
                                             connect_current_combo,
                                             connect_value)


class ScatterLayerStyleWidget(QtGui.QWidget):

    # Size-related GUI elements
    size_mode = CurrentComboTextProperty('ui.combo_size_mode')
    size_attribute = CurrentComboProperty('ui.combo_size_attribute')
    size_vmin = FloatLineProperty('ui.value_size_vmin')
    size_vmax = FloatLineProperty('ui.value_size_vmax')
    size = FloatLineProperty('ui.value_fixed_size')

    try:
        size_scaling = ValueProperty('ui.slider_size_scaling', value_range=(0.1, 10), log=True)
    except TypeError:  # Glue < 0.8
        size_scaling = ValueProperty('ui.slider_size_scaling')

    # Color-related GUI elements
    color_mode = CurrentComboTextProperty('ui.combo_color_mode')
    cmap_attribute = CurrentComboProperty('ui.combo_cmap_attribute')
    cmap_vmin = FloatLineProperty('ui.value_cmap_vmin')
    cmap_vmax = FloatLineProperty('ui.value_cmap_vmax')
    cmap = CurrentComboProperty('ui.combo_cmap')
    alpha = ValueProperty('ui.slider_alpha')

    def __init__(self, layer_artist):

        super(ScatterLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # Set up size and color options
        self._setup_size_options()
        self._setup_color_options()
        self._connect_global()

        # Set initial values
        self.layer_artist.size = self.layer.style.markersize
        self.layer_artist.size_scaling = 1
        self.layer_artist.size_mode = 'fixed'
        self.size_mode = 'Fixed'
        self.layer_artist.color = self.layer.style.color
        self.layer_artist.alpha = self.layer.style.alpha
        self.layer_artist.color_mode = 'fixed'
        self.color_mode = 'Fixed'
        self.ui.combo_size_attribute.setCurrentIndex(0)
        self.ui.combo_cmap_attribute.setCurrentIndex(0)
        self.ui.combo_cmap.setCurrentIndex(0)
        self.layer_artist.visible = True

        self._update_size_mode()
        self._update_color_mode()

    def _connect_global(self):
        connect_float_edit(self.layer.style, 'markersize', self.ui.value_fixed_size)
        connect_color(self.layer.style, 'color', self.ui.label_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

    def _disconnect_global(self):
        # FIXME: Requires the ability to disconnect connections
        pass

    def _setup_size_options(self):

        # Set up attribute list
        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_size_attribute, label_data)

        # Set up connections with layer artist
        connect_float_edit(self.layer_artist, 'size', self.ui.value_fixed_size)
        connect_current_combo(self.layer_artist, 'size_attribute', self.ui.combo_size_attribute)
        connect_float_edit(self.layer_artist, 'size_vmin', self.ui.value_size_vmin)
        connect_float_edit(self.layer_artist, 'size_vmax', self.ui.value_size_vmax)
        connect_value(self.layer_artist, 'size_scaling', self.ui.slider_size_scaling, value_range=(0.1, 10), log=True)

        # Set up internal connections
        self.ui.combo_size_mode.currentIndexChanged.connect(self._update_size_mode)
        self.ui.combo_size_attribute.currentIndexChanged.connect(self._update_size_limits)
        self.ui.button_flip_size.clicked.connect(self._flip_size)

    def _update_size_mode(self):

        self.layer_artist.size_mode = self.size_mode.lower()

        if self.size_mode == "Fixed":
            self.ui.size_row_2.hide()
            self.ui.combo_size_attribute.hide()
            self.ui.value_fixed_size.show()
        else:
            self.ui.value_fixed_size.hide()
            self.ui.combo_size_attribute.show()
            self.ui.size_row_2.show()

    def _update_size_limits(self):

        if not hasattr(self, '_size_limits'):
            self._size_limits = {}

        if self.size_attribute in self._size_limits:
            self.size_vmin, self.size_vmax = self._size_limits[self.size_attribute]
        else:
            self.size_vmin, self.size_vmax = self.default_limits(self.size_attribute)
            self._size_limits[self.size_attribute] = self.size_vmin, self.size_vmax

    def _flip_size(self):
        self.size_vmin, self.size_vmax = self.size_vmax, self.size_vmin

    def _setup_color_options(self):

        # Set up attribute list
        label_data = [(comp.label, comp) for comp in self.visible_components]
        update_combobox(self.ui.combo_cmap_attribute, label_data)

        # Set up connections with layer artist
        connect_color(self.layer_artist, 'color', self.ui.label_color)
        connect_current_combo(self.layer_artist, 'cmap_attribute', self.ui.combo_cmap_attribute)
        connect_float_edit(self.layer_artist, 'cmap_vmin', self.ui.value_cmap_vmin)
        connect_float_edit(self.layer_artist, 'cmap_vmax', self.ui.value_cmap_vmax)
        connect_current_combo(self.layer_artist, 'cmap', self.ui.combo_cmap)
        connect_value(self.layer_artist, 'alpha', self.ui.slider_alpha, value_range=(0, 1))

        # Set up internal connections
        self.ui.combo_color_mode.currentIndexChanged.connect(self._update_color_mode)
        self.ui.combo_cmap_attribute.currentIndexChanged.connect(self._update_cmap_limits)
        self.ui.button_flip_cmap.clicked.connect(self._flip_cmap)

    def _update_color_mode(self):

        self.layer_artist.color_mode = self.color_mode.lower()

        if self.color_mode == "Fixed":
            self.ui.color_row_2.hide()
            self.ui.color_row_3.hide()
            self.ui.combo_cmap_attribute.hide()
            self.ui.spacer_color_label.show()
            self.ui.label_color.show()
        else:
            self.ui.label_color.hide()
            self.ui.combo_cmap_attribute.show()
            self.ui.spacer_color_label.hide()
            self.ui.color_row_2.show()
            self.ui.color_row_3.show()

    def _update_cmap_limits(self):

        if not hasattr(self, '_cmap_limits'):
            self._cmap_limits = {}

        if self.cmap_attribute in self._cmap_limits:
            self.cmap_vmin, self.cmap_vmax = self._cmap_limits[self.cmap_attribute]
        else:
            self.cmap_vmin, self.cmap_vmax = self.default_limits(self.cmap_attribute)
            self._cmap_limits[self.cmap_attribute] = self.cmap_vmin, self.cmap_vmax

    def _flip_cmap(self):
        self.cmap_vmin, self.cmap_vmax = self.cmap_vmax, self.cmap_vmin

    def default_limits(self, attribute):
        # For subsets, we want to compute the limits based on the full
        # dataset not just the subset.
        if isinstance(self.layer, Subset):
            vmin = np.nanmin(self.layer.data[attribute])
            vmax = np.nanmax(self.layer.data[attribute])
        else:
            vmin = np.nanmin(self.layer[attribute])
            vmax = np.nanmax(self.layer[attribute])
        return vmin, vmax

    @property
    def visible_components(self):
        if isinstance(self.layer, Subset):
            return self.layer.data.visible_components
        else:
            return self.layer.visible_components


if __name__ == "__main__":

    from glue.external.qt import get_qapp
    from glue.external.echo import CallbackProperty

    app = get_qapp()

    class Style(object):
        color = CallbackProperty("#334455")
        alpha = CallbackProperty(1.0)
        markersize = CallbackProperty(4)

    class Component(object):
        def __init__(self, label):
            self.label = label

    c1 = Component('a')
    c2 = Component('b')
    c3 = Component('c')

    class Layer(object):
        style = Style()
        visible_components = [c1, c2, c3]

    class LayerArtist(object):
        layer = Layer()

        size_mode = CallbackProperty(None)
        size = CallbackProperty()
        size_attribute = CallbackProperty()
        size_vmin = CallbackProperty()
        size_vmax = CallbackProperty()
        size_scaling = CallbackProperty()

        color_mode = CallbackProperty(None)
        color = CallbackProperty()
        cmap_attribute = CallbackProperty()
        cmap_vmin = CallbackProperty()
        cmap_vmax = CallbackProperty()
        cmap = CallbackProperty()
        alpha = CallbackProperty()

    layer_artist = LayerArtist()

    widget = ScatterLayerStyleWidget(layer_artist)
    widget.show()

    app.exec_()
