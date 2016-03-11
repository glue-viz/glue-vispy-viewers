import os

import numpy as np

from glue.external.qt import QtCore, QtGui
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState
from glue.icons.qt import get_icon
from glue.utils import nonpartial
from glue.core import Data

POINT_ICON = os.path.join(os.path.dirname(__file__), 'glue_point.png')


class VispyDataViewerToolbar(QtGui.QToolBar):

    def __init__(self, vispy_widget=None, parent=None):

        super(VispyDataViewerToolbar, self).__init__(parent=parent)

        # Keep a reference to the Vispy Widget and the Vispy Data Viewer
        self._vispy_widget = vispy_widget
        self._vispy_data_viewer = parent
        self._data_collection = parent._data

        # Set visual preferences
        self.setIconSize(QtCore.QSize(25, 25))

        # Set up selection actions

        a = QtGui.QAction(get_icon('glue_lasso'), 'Lasso Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_lasso))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.lasso_action = a

        a = QtGui.QAction(get_icon('glue_square'), 'Rectangle Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_rectangle))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.rectangle_action = a

        # TODO: change path to icon once it's in a released version of glue
        a = QtGui.QAction(QtGui.QIcon(POINT_ICON), 'Point Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_point))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.point_action = a

        # Connect callback functions to VisPy Canvas
        self._vispy_widget.canvas.events.mouse_press.connect(self.on_mouse_press)
        self._vispy_widget.canvas.events.mouse_release.connect(self.on_mouse_release)
        self._vispy_widget.canvas.events.mouse_move.connect(self.on_mouse_move)

    def toggle_lasso(self):
        if self.lasso_action.isChecked():
            self.mode = 'lasso'
            self.rectangle_action.setChecked(False)
            self.point_action.setChecked(False)
        else:
            self.mode = None

    def toggle_rectangle(self):
        if self.rectangle_action.isChecked():
            self.mode = 'rectangle'
            self.lasso_action.setChecked(False)
            self.point_action.setChecked(False)
        else:
            self.mode = None

    def toggle_point(self):
        if self.point_action.isChecked():
            self.mode = 'point'
            self.lasso_action.setChecked(False)
            self.rectangle_action.setChecked(False)
        else:
            self.mode = None

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        if value is None:
            self.enable_camera_events()
        else:
            self.disable_camera_events()

    @property
    def camera(self):
        return self._vispy_widget.view.camera

    def enable_camera_events(self):
        self.camera._viewbox.events.mouse_move.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_press.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_release.connect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_wheel.connect(self.camera.viewbox_mouse_event)

    def disable_camera_events(self):
        self.camera._viewbox.events.mouse_move.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_press.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_release.disconnect(self.camera.viewbox_mouse_event)
        self.camera._viewbox.events.mouse_wheel.disconnect(self.camera.viewbox_mouse_event)

    def on_mouse_press(self, event):
        # TODO: here we need to start a new selection shape based on the mode
        pass

    def on_mouse_move(self, event):
        # TODO: here we need to update the selection shape based on the mode
        pass

    def on_mouse_release(self, event):

        # TODO: here we need to finalize the selection shape based on the mode

        # Get the component IDs
        x_att = self._vispy_widget.options.x_att
        y_att = self._vispy_widget.options.y_att
        z_att = self._vispy_widget.options.z_att

        # Get the visible datasets
        visible_data = self.get_visible_data()

        # TODO: here we need to get a mask for the selection, which we assume
        # will be called ``mask``. For now, we set the mask to a random mask.
        mask = np.random.random(visible_data[0].shape) > 0.5

        # We now make a subset state. For scatter plots we'll want to use an
        # ElementSubsetState, while for cubes, we'll need to change to a
        # MaskSubsetState.
        subset_state = ElementSubsetState(np.where(mask)[0])

        # We now check what the selection mode is, and update the selection as
        # needed (this is delegated to the correct subset mode).
        mode = EditSubsetMode()
        focus = visible_data[0] if len(visible_data) > 0 else None
        mode.update(self._data_collection, subset_state, focus_data=focus)

    def get_visible_data(self):
        """
        Returns all the visible data objects in the viewer
        """
        visible = []
        # Loop over visible layer artists
        for layer_artist in self._vispy_data_viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        return visible
