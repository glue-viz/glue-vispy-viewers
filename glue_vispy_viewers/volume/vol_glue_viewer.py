from glue.qt.widgets.data_viewer import DataViewer
from glue.core import message as msg

from .vol_vispy_widget import QtVispyWidget
from .options_widget import VolumeOptionsWidget


class GlueVispyViewer(DataViewer):

    LABEL = "3D Volume Rendering"

    def __init__(self, session, parent=None):

        super(GlueVispyViewer, self).__init__(session, parent=parent)

        self._vispy_widget = QtVispyWidget()
        self._canvas = self._vispy_widget.canvas
        self.viewer_size = [600, 400]
        self._canvas.size = self.viewer_size
        self.setCentralWidget(self._canvas.native)

        self._data = None
        self._subsets = []
        self._options_widget = VolumeOptionsWidget(vispy_widget=self._vispy_widget)

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
        self.data = data
        self._update_data()
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
        self._vispy_widget.set_subsets([{'mask': s.to_mask(),
                                         'color': s.style.color,
                                         'alpha': s.style.alpha} for s in self._subsets])
        self._redraw()

    def _redraw(self):
        self._vispy_widget.canvas.render()

    @property
    def window_title(self):
        c = self.client.component
        if c is not None:
            label = str(c.label)
        else:
            label = '3D Volume'
        return label

    # Add side panels
    # def layer_view(self):
    #     return self._layer_view

    def add_subset(self, subset):
        pass

    def restore_layers(self, rec, context):
        pass

    def notify(self, message):
        pass

    def options_widget(self):
        return self._options_widget
