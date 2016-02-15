from __future__ import absolute_import, division, print_function

import os

from glue.core.subset import Subset
from matplotlib.colors import colorConverter

from glue.external.qt import QtGui
from glue.utils.qt import load_ui, mpl_to_qt4_color, qt4_to_mpl_color, update_combobox
from glue.utils.qt.widget_properties import ValueProperty, CurrentComboProperty, FloatLineProperty, connect_value
from glue.external.echo import add_callback


class ScatterLayerStyleWidget(QtGui.QWidget):

    attribute = CurrentComboProperty('ui.combo_attribute')
    vmin = FloatLineProperty('ui.value_min')
    vmax = FloatLineProperty('ui.value_max')
    alpha = ValueProperty('ui.slider_alpha')

    def __init__(self, layer_artist):

        super(ScatterLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        self._setup_attribute_combo()
        self._setup_color_label()

        self._limits = {}

        # Set up connections
        self.ui.slider_alpha.valueChanged.connect(self._update_alpha)
        add_callback(self.layer.style, 'color', self._update_color)
        connect_value(self.layer.style, 'alpha', self.ui.slider_alpha, scaling=1./100.)

        # Set initial values
        self._update_color(self.layer.style.color)
        self._update_alpha()
        self.layer_artist.visible = True

    def _setup_attribute_combo(self):
        """
        Set up the combo box with the list of attributes
        """
        if isinstance(self.layer, Subset):
            visible_components = self.layer.data.visible_components
        else:
            visible_components = self.layer.visible_components
        labels = [(comp.label, comp) for comp in visible_components]
        update_combobox(self.ui.combo_attribute, labels)

    def _setup_color_label(self):
        """
        Set up the label used to display the selected color
        """
        self.label_color.mousePressed.connect(self.query_color)

    def query_color(self, *args):
        color = QtGui.QColorDialog.getColor(self._current_qcolor, self.label_color)
        if color.isValid():
            # The following should trigger the calling of _update_color, so
            # we don't need to call it explicitly
            self.layer.style.color = qt4_to_mpl_color(color)

    def _update_color(self, value):

        # Update the color box
        qcolor = mpl_to_qt4_color(self.layer.style.color)
        im = QtGui.QImage(80, 20, QtGui.QImage.Format_RGB32)
        im.fill(qcolor)
        pm = QtGui.QPixmap.fromImage(im)
        self.label_color.setPixmap(pm)
        self._current_qcolor = qcolor

        # Update the colormap for the visualization
        rgb = colorConverter.to_rgb(value)
        self.layer_artist.set_color(rgb)

    def _update_alpha(self):
        # TODO: add scaling to ValueProperty
        self.layer_artist.set_alpha(self.alpha / 100.)
