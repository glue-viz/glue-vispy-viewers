try:
    from glue.viewers.common.qt.data_viewer import DataViewer
except ImportError:
    from glue.qt.widgets.data_viewer import DataViewer

from glue.core import message as msg
from glue.external.qt import QtGui

from ..common.viewer_options import VispyOptionsWidget
from ..common.vispy_viewer import VispyWidget
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget


class VispyVolumeViewer(DataViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = VolumeLayerStyleWidget

    def __init__(self, session, parent=None):

        super(VispyVolumeViewer, self).__init__(session, parent=parent)

        self._vispy_widget = VispyWidget()
        self.setCentralWidget(self._vispy_widget)

        self._options_widget = VispyOptionsWidget(vispy_widget=self._vispy_widget)

    def register_to_hub(self, hub):

        super(VispyVolumeViewer, self).register_to_hub(hub)

        def subset_has_data(x):
            return x.sender.data in self._layer_artist_container.layers

        def has_data(x):
            return x.sender in self._layer_artist_container.layers

        has_data_collection = lambda x: x.sender is self._data

        hub.subscribe(self, msg.SubsetCreateMessage,
                      handler=self._add_subset,
                      filter=subset_has_data)

        hub.subscribe(self, msg.SubsetUpdateMessage,
                      handler=self._update_subset,
                      filter=subset_has_data)

        hub.subscribe(self, msg.SubsetDeleteMessage,
                      handler=self._remove_subset,
                      filter=subset_has_data)

        hub.subscribe(self, msg.DataUpdateMessage,
                      handler=self.update_window_title,
                      filter=has_data)

        hub.subscribe(self, msg.ComponentsChangedMessage,
                      handler=self._update_data,
                      filter=has_data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        layer_artist = VolumeLayerArtist(data, vispy_viewer=self._vispy_widget)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        return True

    def _add_subset(self, message):

        if message.subset in self._layer_artist_container:
            return

        if message.subset.to_mask().ndim != 3:
            return

        layer_artist = VolumeLayerArtist(message.subset, vispy_viewer=self._vispy_widget)
        self._layer_artist_container.append(layer_artist)

    def _update_subset(self, message):
        if message.subset in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.subset]:
                layer_artist._update_data()
            self._vispy_widget.canvas.update()

    def _remove_subset(self, message):
        if message.subset in self._layer_artist_container:
            self._layer_artist_container.pop(message.subset)
            self._vispy_widget.canvas.update()

    def _update_data(self):
        self._vispy_widget.data = self.data
        self._vispy_widget.add_volume_visual()
        self._redraw()

    def _redraw(self):
        self._vispy_widget.canvas.render()

    @property
    def window_title(self):
        return "3D Volume Rendering"

    def update_window_title(self, *args):
        pass

    def options_widget(self):
        return self._options_widget
