from __future__ import absolute_import, division, print_function

import sys

try:
    from glue.viewers.common.qt.data_viewer import DataViewer
except ImportError:
    from glue.qt.widgets.data_viewer import DataViewer

from glue.core import message as msg
from glue.utils import nonpartial
from glue.core.state import lookup_class_with_patches

from qtpy import PYQT5, QtWidgets

from .vispy_widget import VispyWidgetHelper
from .viewer_options import VispyOptionsWidget
from .toolbar import VispyViewerToolbar
from .viewer_state import Vispy3DViewerState
from .compat import update_viewer_state

BROKEN_PYQT5_MESSAGE = ("The version of PyQt5 you are using does not appear to "
                        "support OpenGL. See <a href='http://www.google.com'>this page</a> for "
                        "more information about fixing this.")


class BaseVispyViewer(DataViewer):

    _state_cls = Vispy3DViewerState
    _toolbar_cls = VispyViewerToolbar

    tools = ['vispy:reset', 'vispy:save', 'vispy:rotate']

    # If imageio is available, we can add the record icon
    try:
        import imageio  # noqa
    except ImportError:
        pass
    else:
        tools.insert(1, 'vispy:record')

    def __init__(self, session, viewer_state=None, parent=None):

        super(BaseVispyViewer, self).__init__(session, parent=parent)

        self.state = viewer_state or self._state_cls()

        self._vispy_widget = VispyWidgetHelper(viewer_state=self.state)

        self.setCentralWidget(self._vispy_widget.canvas.native)

        self._options_widget = VispyOptionsWidget(parent=self, viewer_state=self.state)

        self.state.add_callback('clip_data', nonpartial(self._toggle_clip))

        self.status_label = None
        self.client = None
        self._opengl_ok = None

        # When layer artists are removed from the layer artist container, we need
        # to make sure we remove matching layer states in the viewer state
        # layers attribute.
        self._layer_artist_container.on_changed(nonpartial(self._sync_state_layers))

    def paintEvent(self, *args, **kwargs):
        super(BaseVispyViewer, self).paintEvent(*args, **kwargs)
        if self._opengl_ok is None:
            self._opengl_ok = self._vispy_widget.canvas.native.context() is not None
            if not self._opengl_ok:
                QtWidgets.QMessageBox.critical(self, "Error", BROKEN_PYQT5_MESSAGE)
                self.close(warn=False)
                self._vispy_widget.canvas.native.close()

    def _sync_state_layers(self):
        # Remove layer state objects that no longer have a matching layer
        for layer_state in self.state.layers:
            if layer_state.layer not in self._layer_artist_container:
                self.state.layers.remove(layer_state)

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

        hub.subscribe(self, msg.NumericalDataChangedMessage,
                      handler=self._numerical_data_changed,
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

    # instance by object viewers later
    def add_data(self, data):
        return True

    def _add_subset(self, message):
        pass

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

    def _numerical_data_changed(self, message):
        for layer_artist in self._layer_artist_container:
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
        return dict(state=self.state.__gluestate__(context),
                    session=context.id(self._session),
                    size=self.viewer_size,
                    pos=self.position,
                    layers=list(map(context.do, self.layers)),
                    _protocol=1)

    @classmethod
    def __setgluestate__(cls, rec, context):

        if rec.get('_protocol', 0) < 1:
            update_viewer_state(rec, context)

        session = context.object(rec['session'])
        viewer = cls(session)
        viewer.register_to_hub(session.hub)
        viewer.viewer_size = rec['size']
        x, y = rec['pos']
        viewer.move(x=x, y=y)

        viewer_state = cls._state_cls.__setgluestate__(rec['state'], context)
        viewer.state.update_from_state(viewer_state)

        # Restore layer artists
        for l in rec['layers']:
            cls = lookup_class_with_patches(l.pop('_type'))
            layer_state = context.object(l['state'])
            layer_artist = cls(viewer, layer_state=layer_state)
            viewer._layer_artist_container.append(layer_artist)

        return viewer

    def show_status(self, text):
        statusbar = self.statusBar()
        statusbar.showMessage(text)

    def restore_layers(self, layers, context):
        pass

    def _toggle_clip(self):
        for layer_artist in self._layer_artist_container:
            if self.state.clip_data:
                layer_artist.set_clip(self.state.clip_limits)
            else:
                layer_artist.set_clip(None)

    if PYQT5:

        def show(self):

            # WORKAROUND:
            # Due to a bug in Qt5, a hidden toolbar in glue causes a grey
            # rectangle to be overlaid on top of the glue window. Therefore
            # we check if the toolbar is hidden, and if so we make it into a
            # floating toolbar temporarily - still hidden, so this will not
            # be noticeable to the user.

            # tbar.setAllowedAreas(Qt.NoToolBarArea)

            from qtpy.QtCore import Qt

            tbar = self._session.application._mode_toolbar
            hidden = tbar.isHidden()

            if hidden:
                original_flags = tbar.windowFlags()
                tbar.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

            super(BaseVispyViewer, self).show()

            if hidden:
                tbar.setWindowFlags(original_flags)
                tbar.hide()
