import os

import numpy as np
from vispy import app, scene
from matplotlib import path

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

        # Initialize drawing visual
        self.line_pos = []
        self.line = scene.visuals.Line(color='white', method='gl', parent=self._vispy_widget.canvas.scene)

        # Selection defaults
        self.selection_origin = (0, 0)
        self.selected = []


        # TODO: I need to set the 'tr' but how can I get the current visual?
        # also the data_collection should be related with the x, y, z attributes selected by the user

        # self.white = (1.0, 1.0, 1.0, 1.0)
        # self.black = (0.0, 0.0, 0.0, 0.0)
        # self.facecolor = facecolor

        # Scatter plot data, visual and projection
        #  = self._data_collection
        # self._scatter = scatter
        # self.tr = self._scatter.node_transform(self._view)

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
        """
        Realize picking functionality and set origin mouse pos
        """
        if event.button == 1 and self.mode is not None:
            tr = self._vispy_widget.get_tr()
            if self.mode is 'point':
                # Ray intersection on the CPU to highlight the selected point(s)
                data = tr.map(self._data_collection)[:, :2]
                m1 = data > (event.pos - 4)
                m2 = data < (event.pos + 4)

                self.selected = np.argwhere(m1[:, 0] & m1[:, 1] & m2[:, 0] & m2[:, 1])

                # self.mark_selected()
                print('point get', self.selected)
            else:
                self.selection_origin = event.pos

    def on_mouse_move(self, event):
        # TODO: here we need to update the selection shape based on the mode
        """
        Draw selection line along dragging mouse
        """
        if event.button == 1 and event.is_dragging and self.mode is not None:
            if self.mode is 'lasso':
                self.line_pos.append(event.pos)
                self.line.set_data(np.array(self.line_pos))

            if self.mode is 'rectangle':
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                center = (width / 2. + self.selection_origin[0], height / 2. + self.selection_origin[1], 0)
                self.line_pos = self.rectangle_vertice(center, height, width)
                self.line.set_data(np.array(self.line_pos))

                # if self.selection_id == '2':
                self.line_pos = self.rectangle_vertice(center, height, width)
                self.line.set_data(np.array(self.line_pos))
                #
                # if self.selection_id == '3':
                #     self.line_pos = self.ellipse_vertice(center, radius=(np.abs(width / 2.), np.abs(height / 2.)),
                #                                          start_angle=0., span_angle=360., num_segments=500)
                #     self.line.set_data(pos=np.array(self.line_pos), connect='strip')

    def on_mouse_release(self, event):

        # TODO: here we need to finalize the selection shape based on the mode

        # Get the component IDs
        x_att = self._vispy_widget.options.x_att
        y_att = self._vispy_widget.options.y_att
        z_att = self._vispy_widget.options.z_att

        # Get the visible datasets
        visible_data = self.get_visible_data()
        print('whats visible_data', visible_data)

        if event.button == 1 and self.mode is not None and self.mode is not 'point':
            # self.facecolor[self.facecolor[:, 1] != 1.0] = self.white
            tr = self._vispy_widget.get_tr()

            data = tr.map(self._data_collection)[:, :2]

            selection_path = path.Path(self.line_pos, closed=True)
            mask = [selection_path.contains_points(data)]

            # self.selected = mask
            # self.mark_selected()

            # TODO: here we need to get a mask for the selection, which we assume
            # will be called ``mask``. For now, we set the mask to a random mask.
            # mask = np.random.random(visible_data[0].shape) > 0.5

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

    def mark_selected(self):
        # self.facecolor[self.facecolor[:, 1] != 1.0] = self.white
        # self._scatter.set_data(, face_color=self.facecolor)
        # for i in self.selected:
        #     self.facecolor[i] = [1.0, 0.0, 0.0, 1]
        #
        # self._scatter.set_data(, face_color=self.facecolor)
        # self._scatter.update()
        # TODO: add points picking action here
        pass

    def rectangle_vertice(self, center, height, width):
        """
        Borrow from _generate_vertices in vispy/visuals/rectangle.py
        """
        half_height = height / 2.
        half_width = width / 2.

        bias1 = np.ones(4) * half_width
        bias2 = np.ones(4) * half_height

        corner1 = np.empty([1, 3], dtype=np.float32)
        corner2 = np.empty([1, 3], dtype=np.float32)
        corner3 = np.empty([1, 3], dtype=np.float32)
        corner4 = np.empty([1, 3], dtype=np.float32)

        corner1[:, 0] = center[0] - bias1[0]
        corner1[:, 1] = center[1] - bias2[0]
        corner1[:, 2] = 0

        corner2[:, 0] = center[0] + bias1[1]
        corner2[:, 1] = center[1] - bias2[1]
        corner2[:, 2] = 0

        corner3[:, 0] = center[0] + bias1[2]
        corner3[:, 1] = center[1] + bias2[2]
        corner3[:, 2] = 0

        corner4[:, 0] = center[0] - bias1[3]
        corner4[:, 1] = center[1] + bias2[3]
        corner4[:, 2] = 0

        # Get vertices between each corner of the rectangle for border drawing
        vertices = np.concatenate(([[center[0], center[1], 0.]],
                                   [[center[0] - half_width, center[1], 0.]],
                                   corner1,
                                   [[center[0], center[1] - half_height, 0.]],
                                   corner2,
                                   [[center[0] + half_width, center[1], 0.]],
                                   corner3,
                                   [[center[0], center[1] + half_height, 0.]],
                                   corner4,
                                   [[center[0] - half_width, center[1], 0.]]))

        # vertices = np.array(output, dtype=np.float32)
        return vertices[1:, ..., :2]
