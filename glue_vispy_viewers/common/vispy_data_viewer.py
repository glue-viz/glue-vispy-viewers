try:
    from glue.viewers.common.qt.data_viewer import DataViewer
except ImportError:
    from glue.qt.widgets.data_viewer import DataViewer

from glue.core import message as msg

from .vispy_widget import VispyWidget
from .viewer_options import VispyOptionsWidget


class BaseVispyViewer(DataViewer):

    def __init__(self, session, parent=None):

        super(BaseVispyViewer, self).__init__(session, parent=parent)

        self._vispy_widget = VispyWidget()
        self.setCentralWidget(self._vispy_widget)

        self._options_widget = VispyOptionsWidget(vispy_widget=self._vispy_widget)

    def register_to_hub(self, hub):

        super(BaseVispyViewer, self).register_to_hub(hub)

        def subset_has_data(x):
            return x.sender.data in self._layer_artist_container.layers

        def has_data(x):
            return x.sender in self._layer_artist_container.layers

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

    def update_window_title(self, *args):
        pass

    def options_widget(self):
        return self._options_widget

    @property
    def window_title(self):
        return self.LABEL
