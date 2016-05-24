try:
    from glue.viewers.common.qt.data_viewer import DataViewer
except ImportError:
    from glue.qt.widgets.data_viewer import DataViewer

from glue.core import message as msg
from glue.core import Data

from .vispy_widget import VispyWidget
from .viewer_options import VispyOptionsWidget


class BaseVispyViewer(DataViewer):

    def __init__(self, session, parent=None):

        super(BaseVispyViewer, self).__init__(session, parent=parent)

        self._vispy_widget = VispyWidget()
        self.setCentralWidget(self._vispy_widget)

        self._options_widget = VispyOptionsWidget(vispy_widget=self._vispy_widget, data_viewer=self)

        toolbar = self._toolbar_cls(vispy_widget=self._vispy_widget, parent=self)
        self.addToolBar(toolbar)

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

        def is_appearance_settings(msg):
            return ('BACKGROUND_COLOR' in msg.settings or
                    'FOREGROUND_COLOR' in msg.settings)

        hub.subscribe(self, msg.SettingsChangeMessage,
                      handler=self._update_appearance_from_settings,
                      filter=is_appearance_settings)

    def unregister(self, hub):
        super(BaseVispyViewer, self).unregister(hub)
        hub.unsubscribe_all(self)

    def _update_appearance_from_settings(self, message):
        self._vispy_widget._update_appearance_from_settings()

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

    def _update_data(self, message):
        if message.data in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.data]:
                layer_artist._update_data()

    def _redraw(self):
        self._vispy_widget.canvas.render()

    def update_window_title(self, *args):
        pass

    def options_widget(self):
        return self._options_widget

    @property
    def window_title(self):
        return self.LABEL

    def __gluestate__(self, context):
        state = super(BaseVispyViewer, self).__gluestate__(context)
        state['options'] = self._options_widget.__gluestate__(context)
        return state

    @classmethod
    def __setgluestate__(cls, rec, context):

        viewer = super(BaseVispyViewer, cls).__setgluestate__(rec, context)

        from ..scatter.layer_artist import ScatterLayerArtist

        for layer_artist in viewer.layers:
            if isinstance(layer_artist, ScatterLayerArtist) and isinstance(layer_artist.layer, Data):
                viewer._options_widget._update_attributes_from_data(layer_artist.layer)

        for attr in sorted(rec['options'], key=lambda x: 0 if 'att' in x else 1):
            value = rec['options'][attr]
            setattr(viewer._options_widget, attr, context.object(value))

        return viewer
