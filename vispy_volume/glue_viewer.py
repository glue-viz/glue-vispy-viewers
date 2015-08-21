import numpy as np

from glue.qt.widgets.data_viewer import DataViewer
from glue.core import message as msg

# Add a __init__.py file to this folder can solve the relative import problem
from .vispy_widget import QtVispyWidget
from .options_widget import VolumeOptionsWidget

class GlueVispyViewer(DataViewer):

    LABEL = "3D Volume"

    def __init__(self, session, parent=None):
        super(GlueVispyViewer, self).__init__(session, parent=parent)
        self._vispy_widget = QtVispyWidget()
        self.setCentralWidget(self._vispy_widget.canvas.native)
        self._data = None
        self._subsets = []
        # self._layer_view = onewidget()
        self._options_widget = VolumeOptionsWidget()

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

    def add_data(self, data):
        self._data = data['PRIMARY']
        initial_level = "{0:.3g}".format(np.nanpercentile(data['PRIMARY'], 99))
        self._options_widget.levels = initial_level
        self._options_widget.update_viewer()
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
        self._vispy_widget.set_data(self._data)
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

    # Add side panels
    '''def layer_view(self):

        return self._layer_view'''

    def options_widget(self):
        return self._options_widget
