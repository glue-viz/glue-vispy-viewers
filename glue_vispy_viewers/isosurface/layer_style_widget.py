from __future__ import absolute_import, division, print_function

import os

import numpy as np

from glue.core.subset import Subset

from qtpy import QtWidgets

from glue.utils.qt import load_ui
from glue.external.echo.qt import autoconnect_callbacks_to_qt
from glue.core.qt.data_combo_helper import ComponentIDComboHelper


class IsosurfaceLayerStyleWidget(QtWidgets.QWidget):

    def __init__(self, layer_artist):

        super(IsosurfaceLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.state = layer_artist.state

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        # TODO: the following (passing self.layer to data_collection as second argument)
        # is a hack and we need to figure out a better solution.
        self.att_helper = ComponentIDComboHelper(self.ui.combodata_attribute, self.layer)
        self.att_helper.append_data(self.layer)

        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.)),
                          'value_step': dict(value_range=(1, 10))}
        autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)


if __name__ == "__main__":

    from glue.utils.qt import get_qapp
    from glue.external.echo import CallbackProperty

    app = get_qapp()

    class Style(object):
        # TODO: need a cmap here
        cmap = CallbackProperty(get_colormap('autumn'))
        # alpha = CallbackProperty(1.0)
        # markersize = CallbackProperty(4)

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

        attribute = CallbackProperty()
        level_low = CallbackProperty()
        level_high = CallbackProperty()
        # We don't have IntLineProperty?
        cmap = CallbackProperty()
        step = CallbackProperty()
        step_value = CallbackProperty()


    layer_artist = LayerArtist()

    widget = IsosurfaceLayerStyleWidget(layer_artist)
    widget.show()

    app.exec_()
