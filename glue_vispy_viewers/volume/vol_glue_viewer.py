try:
    from glue.viewers.common.qt.data_viewer import DataViewer
except ImportError:
    from glue.qt.widgets.data_viewer import DataViewer

from glue.core import message as msg

from ..common.viewer_options import VispyOptionsWidget
from ..common.vispy_viewer import VispyWidget
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget


class GlueVispyViewer(DataViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = VolumeLayerStyleWidget

    def __init__(self, session, parent=None):

        super(GlueVispyViewer, self).__init__(session, parent=parent)

        self._vispy_widget = VispyWidget()
        self.setCentralWidget(self._vispy_widget)

        self._options_widget = VispyOptionsWidget(vispy_widget=self._vispy_widget)

    def register_to_hub(self, hub):

        super(GlueVispyViewer, self).register_to_hub(hub)

        dfilter = lambda x: True
        dcfilter = lambda x: True
        subfilter = lambda x: True

        hub.subscribe(self, msg.SubsetCreateMessage,
                      handler=self._add_subset,
                      filter=dfilter)

        hub.subscribe(self, msg.SubsetUpdateMessage,
                      handler=self._update_subset,
                      filter=subfilter)

        hub.subscribe(self, msg.SubsetDeleteMessage,
                      handler=self._remove_subset)

        hub.subscribe(self, msg.DataUpdateMessage,
                      handler=self.update_window_title)

        hub.subscribe(self, msg.ComponentsChangedMessage,
                      handler=self._update_data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def add_data(self, data):

        layer_artist = VolumeLayerArtist(data, vispy_viewer=self._vispy_widget)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)
        return True

    def _add_subset(self, message):
        self._subsets.append(message.subset)
        self._update_subsets()

    def _update_subset(self, message):
        self._update_subsets()

    def _remove_subset(self, message):
        self._subsets.remove(message.subset)
        self._update_subsets()

    def _update_data(self):
        self._vispy_widget.data = self.data
        self._vispy_widget.add_volume_visual()
        self._redraw()

    def _update_subsets(self):
        # TODO: in future, we should be smarter and not compute the masks just
        # for style changes, but this will do for now for experimentation.
        self._vispy_widget.set_subsets([{'label': s.label,
                                         'mask': s.to_mask(),
                                         'color': s.style.color,
                                         'alpha': s.style.alpha} for s in self._subsets if s.to_mask().ndim == 3])
        self._redraw()

    def _redraw(self):
        self._vispy_widget.canvas.render()

    @property
    def window_title(self):
        return "3D Volume Rendering"

    def update_window_title(self, *args):
        pass

    def add_subset(self, subset):
        pass

    def restore_layers(self, rec, context):
        pass

    def notify(self, message):
        pass

    def options_widget(self):
        return self._options_widget
