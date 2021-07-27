import os

from qtpy import QtWidgets

from glue.utils.qt import load_ui
from echo.qt import autoconnect_callbacks_to_qt


class IsosurfaceLayerStyleWidget(QtWidgets.QWidget):

    def __init__(self, layer_artist):

        super(IsosurfaceLayerStyleWidget, self).__init__()

        self.ui = load_ui('layer_style_widget.ui', self,
                          directory=os.path.dirname(__file__))

        self.state = layer_artist.state

        self.layer_artist = layer_artist
        self.layer = layer_artist.layer

        connect_kwargs = {'value_alpha': dict(value_range=(0., 1.)),
                          'value_step': dict(value_range=(1, 10))}
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui, connect_kwargs)


# if __name__ == "__main__":
#
#     from glue.utils.qt import get_qapp
#     from echo import CallbackProperty
#
#     app = get_qapp()
#
#     # class Style(object):
#         # TODO: need a cmap here
#         # cmap = CallbackProperty(get_colormap('autumn'))
#         # alpha = CallbackProperty(1.0)
#         # markersize = CallbackProperty(4)
#
#     class Component(object):
#         def __init__(self, label):
#             self.label = label
#
#     c1 = Component('a')
#     c2 = Component('b')
#     c3 = Component('c')
#
#     class Layer(object):
#         style = Style()
#         visible_components = [c1, c2, c3]
#
#     class LayerArtist(object):
#         layer = Layer()
#
#         attribute = CallbackProperty()
#         level_low = CallbackProperty()
#         level_high = CallbackProperty()
#         # We don't have IntLineProperty?
#         cmap = CallbackProperty()
#         step = CallbackProperty()
#         step_value = CallbackProperty()
#
#     layer_artist = LayerArtist()
#
#     widget = IsosurfaceLayerStyleWidget(layer_artist)
#     widget.show()
#
#     app.exec_()
