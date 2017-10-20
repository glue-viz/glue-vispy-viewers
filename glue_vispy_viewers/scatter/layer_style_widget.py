from __future__ import absolute_import, division, print_function

import os

from qtpy import QtWidgets

from glue.utils import nonpartial
from glue.utils.qt import load_ui
from glue.external.echo.qt import autoconnect_callbacks_to_qt

from glue_vispy_viewers.utils import fix_tab_widget_fontsize


class ScatterLayerStyleWidget(QtWidgets.QWidget):

    def __init__(self, layer_artist):

        super(ScatterLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        fix_tab_widget_fontsize(self.ui.tab_widget)

        self.state = layer_artist.state

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.)),
                          'value_size_scaling': dict(value_range=(0.1, 10), log=True)}
        autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)

        # Set initial values
        self._update_size_mode()
        self._update_color_mode()

        self.state.add_callback('color_mode', nonpartial(self._update_color_mode))
        self.state.add_callback('size_mode', nonpartial(self._update_size_mode))

    def _update_size_mode(self):

        if self.state.size_mode == "Fixed":
            self.ui.size_row_2.hide()
            self.ui.combosel_size_attribute.hide()
            self.ui.valuetext_size.show()
        else:
            self.ui.valuetext_size.hide()
            self.ui.combosel_size_attribute.show()
            self.ui.size_row_2.show()

    def _update_color_mode(self):

        if self.state.color_mode == "Fixed":
            self.ui.color_row_2.hide()
            self.ui.color_row_3.hide()
            self.ui.combosel_cmap_attribute.hide()
            self.ui.spacer_color_label.show()
            self.ui.color_color.show()
        else:
            self.ui.color_color.hide()
            self.ui.combosel_cmap_attribute.show()
            self.ui.spacer_color_label.hide()
            self.ui.color_row_2.show()
            self.ui.color_row_3.show()
