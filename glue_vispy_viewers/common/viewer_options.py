import os

from qtpy import QtWidgets

from glue.external.echo.qt import autoconnect_callbacks_to_qt

from glue.utils import nonpartial
from glue.utils.qt import load_ui
from glue.core.qt.data_combo_helper import ComponentIDComboHelper

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

        self.state = viewer_state

        self._att_helpers = {}

        self._attribute_combos = [self.ui.combodata_x_att,
                                  self.ui.combodata_y_att,
                                  self.ui.combodata_z_att]

        self._components = {}

        self.state.add_callback('layers', nonpartial(self._update_attribute_combos))

    def _update_attribute_combos(self):

        for layer in self.state.layers:

            if layer.layer.ndim == 3:
                # We are using either the volume viewer or the isosurface
                # viewer, so the attribute combo boxes should be set using
                # the pixel components.
                self._update_attributes_from_data_pixel(layer.layer)
                return

        # Since we are still here, we must be using the scatter viewer
        datasets = [layer.layer for layer in self.state.layers]
        self._update_attributes_from_data(datasets)

    def _update_attributes_from_data(self, datasets):

        if len(self._att_helpers) == 0:

            for idx, att in enumerate(self._attribute_combos):
                self._att_helpers[att] = ComponentIDComboHelper(att, self._data_collection,
                                                                categorical=False,
                                                                default_index=idx)

        for idx, att in enumerate(self._attribute_combos):
            self._att_helpers[att].set_multiple_data(datasets)

    def _update_attributes_from_data_pixel(self, data):

        z_cid, y_cid, x_cid = data.pixel_component_ids

        self.ui.combodata_x_att.clear()
        self.ui.combodata_x_att.addItem(x_cid.label, x_cid)
        self._components[x_cid] = data.get_component(x_cid)

        self.ui.combodata_y_att.clear()
        self.ui.combodata_y_att.addItem(y_cid.label, y_cid)
        self._components[y_cid] = data.get_component(y_cid)

        self.ui.combodata_z_att.clear()
        self.ui.combodata_z_att.addItem(z_cid.label, z_cid)
        self._components[z_cid] = data.get_component(z_cid)
