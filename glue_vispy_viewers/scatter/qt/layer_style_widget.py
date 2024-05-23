import os

from qtpy import QtWidgets

from glue_qt.utils import load_ui
from echo.qt import autoconnect_callbacks_to_qt

from glue_qt.utils.app import fix_tab_widget_fontsize


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
                          'value_size_scaling': dict(value_range=(0.1, 10), log=True),
                          'vector_scaling': dict(value_range=(0.1, 10), log=True)}
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)

        # Set initial values
        self._update_size_mode()
        self._update_color_mode()
        self._update_error_vis()
        self._update_vector_vis()

        self.state.add_callback('color_mode', self._update_color_mode)
        self.state.add_callback('size_mode', self._update_size_mode)
        self.state.add_callback('xerr_visible', self._update_error_vis)
        self.state.add_callback('yerr_visible', self._update_error_vis)
        self.state.add_callback('zerr_visible', self._update_error_vis)
        self.state.add_callback('vector_visible', self._update_vector_vis)

    def _update_size_mode(self, *args):

        if self.state.size_mode == "Fixed":
            self.ui.size_row_2.hide()
            self.ui.combosel_size_attribute.hide()
            self.ui.valuetext_size.show()
        else:
            self.ui.valuetext_size.hide()
            self.ui.combosel_size_attribute.show()
            self.ui.size_row_2.show()

    def _update_color_mode(self, *args):

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

    def _update_error_vis(self, *args):
        self.ui.combosel_xerr_attribute.setEnabled(self.state.xerr_visible)
        self.ui.combosel_yerr_attribute.setEnabled(self.state.yerr_visible)
        self.ui.combosel_zerr_attribute.setEnabled(self.state.zerr_visible)

    def _update_vector_vis(self, *arg):
        visible = self.state.vector_visible
        self.ui.combosel_vx_attribute.setEnabled(visible)
        self.ui.combosel_vy_attribute.setEnabled(visible)
        self.ui.combosel_vz_attribute.setEnabled(visible)
        self.ui.value_vector_scaling.setEnabled(visible)
        self.ui.combosel_vector_origin.setEnabled(visible)
        self.ui.bool_vector_arrowhead.setEnabled(visible)
