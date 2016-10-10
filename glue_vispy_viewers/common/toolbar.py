import os

import numpy as np
from ..extern.vispy import app, scene, io

from qtpy import QtCore, QtWidgets, QtGui
from qtpy.compat import getsavefilename

from glue.icons.qt import get_icon
from glue.utils import nonpartial

from glue.core import Data
from glue.core.exceptions import IncompatibleAttribute
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState
from glue.config import settings

try:
    import imageio
except ImportError:
    IMAGEIO_INSTALLED = False
else:
    IMAGEIO_INSTALLED = True

POINT_ICON = os.path.join(os.path.dirname(__file__), 'glue_point.png')
ROTATE_ICON = os.path.join(os.path.dirname(__file__), 'glue_rotate.png')
RECORD_START_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_start.png')
RECORD_STOP_ICON = os.path.join(os.path.dirname(__file__), 'glue_record_stop.png')


class PatchedElementSubsetState(ElementSubsetState):

    # TODO: apply this patch to the core glue code

    def __init__(self, data, indices):
        super(PatchedElementSubsetState, self).__init__(indices=indices)
        self._data = data

    def to_mask(self, data, view=None):
        if data in self._data:
            return super(PatchedElementSubsetState, self).to_mask(data, view=view)
        else:
            # TODO: should really be IncompatibleDataException but many other
            # viewers don't recognize this.
            raise IncompatibleAttribute()

    def copy(self):
        return PatchedElementSubsetState(self._data, self._indices)


class VispyDataViewerToolbar(QtWidgets.QToolBar):
    """
    This class is for showing the toolbar UI and drawing selection line on canvas
    """

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
        self.line = scene.visuals.Line(color=settings.FOREGROUND_COLOR,
                                       width=2, method='agg',
                                       parent=self._vispy_widget.canvas.scene)

        # Selection defaults
        self._scatter = None
        self.mode = None
        self.selection_origin = (0, 0)
        self.selected = []

        # Add a timer to control the view rotate
        self.timer = app.Timer(connect=self.rotate)
        self.record_timer = app.Timer(connect=self.record)

        self.writer = None

        a = QtWidgets.QAction(get_icon('glue_filesave'), 'Save', parent)
        a.triggered.connect(nonpartial(self.save_figure))
        a.setToolTip('Save the figure')
        a.setShortcut('Ctrl+Shift+S')
        parent.addAction(a)
        self.addAction(a)
        self.save_action = a

        if IMAGEIO_INSTALLED:
            a = QtWidgets.QAction(QtGui.QIcon(RECORD_START_ICON), 'Record', parent)
            a.triggered.connect(nonpartial(self.toggle_record))
            a.setToolTip('Start/Stop the record')
            a.setCheckable(True)
            parent.addAction(a)
            self.addAction(a)
            self.record_action = a

        a = QtWidgets.QAction(QtGui.QIcon(ROTATE_ICON), 'Rotate View', parent)
        a.triggered.connect(nonpartial(self.toggle_rotate))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.rotate_action = a

        # Set up selection actions
        a = QtWidgets.QAction(get_icon('glue_lasso'), 'Lasso Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_lasso))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.lasso_action = a

        a = QtWidgets.QAction(get_icon('glue_square'), 'Rectangle Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_rectangle))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.rectangle_action = a

        a = QtWidgets.QAction(get_icon('glue_circle'), 'Ellipse Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_ellipse))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.ellipse_action = a

        # TODO: change path to icon once it's in a released version of glue
        a = QtWidgets.QAction(QtGui.QIcon(POINT_ICON), 'Point Selection', parent)
        a.triggered.connect(nonpartial(self.toggle_point))
        a.setCheckable(True)
        parent.addAction(a)
        self.addAction(a)
        self.point_action = a

        # Connect callback functions to VisPy Canvas
        self._vispy_widget.canvas.events.mouse_press.connect(self.on_mouse_press)
        self._vispy_widget.canvas.events.mouse_release.connect(self.on_mouse_release)
        self._vispy_widget.canvas.events.mouse_move.connect(self.on_mouse_move)

    def save_figure(self):
        outfile, file_filter = getsavefilename(caption='Save File',
                                               filters='PNG Files (*.png);;'
                                                       'JPEG Files (*.jpeg);;'
                                                       'TIFF Files (*.tiff);;')

        # This indicates that the user cancelled
        if not outfile:
            return
        img = self._vispy_widget.canvas.render()
        try:
            file_filter = str(file_filter).split()[0]
            io.imsave(outfile, img, format=file_filter)
        except ImportError:
            # TODO: give out a window to notify that only .png file format is supported
            if not '.' in outfile:
                outfile += '.png'
            io.write_png(outfile, img)

    def toggle_record(self):
        if self.record_action.isChecked():
            # pop up a window for file saving
            outfile, file_filter = getsavefilename(caption='Save Animation',
                                                   filters='GIF Files (*.gif);;')
            # This indicates that the user cancelled
            if not outfile:
                self.record_action.blockSignals(True)
                self.record_action.setChecked(False)
                self.record_action.blockSignals(False)
                return
            self.record_action.setIcon(QtGui.QIcon(RECORD_STOP_ICON))
            self.writer = imageio.get_writer(outfile)
            self.record_timer.start(0.1)
        else:
            self.record_timer.stop()
            self.record_action.setIcon(QtGui.QIcon(RECORD_START_ICON))
            self.writer.close()

    def record(self, event):
        if self.writer is not None:
            im = self._vispy_widget.canvas.render()
            self.writer.append_data(im)
        else:
            # maybe better give an option to let user install the package
            print('imageio module needed!')

    def toggle_lasso(self):
        if self.lasso_action.isChecked():
            self.mode = 'lasso'
            self.rectangle_action.setChecked(False)
            self.point_action.setChecked(False)
            self.ellipse_action.setChecked(False)
            self.rotate_action.setChecked(False)
        else:
            self.mode = None

    def toggle_rectangle(self):
        if self.rectangle_action.isChecked():
            self.mode = 'rectangle'
            self.lasso_action.setChecked(False)
            self.point_action.setChecked(False)
            self.ellipse_action.setChecked(False)
            self.rotate_action.setChecked(False)
        else:
            self.mode = None

    def toggle_ellipse(self):
        if self.ellipse_action.isChecked():
            self.mode = 'ellipse'
            self.lasso_action.setChecked(False)
            self.point_action.setChecked(False)
            self.rectangle_action.setChecked(False)
            self.rotate_action.setChecked(False)
        else:
            self.mode = None

    def toggle_point(self):
        if self.point_action.isChecked():
            self.mode = 'point'
            self.lasso_action.setChecked(False)
            self.rectangle_action.setChecked(False)
            self.ellipse_action.setChecked(False)
            self.rotate_action.setChecked(False)
        else:
            self.mode = None

    def toggle_rotate(self):
        if self.rotate_action.isChecked():
            # Start the rotation
            self.timer.start(0.1)
        else:
            self.timer.stop()

    def rotate(self, event):
        self._vispy_widget.view.camera.azimuth -= 1.  # set speed as constant first

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        if value is None:
            self.enable_camera_events()
        else:
            # when the selection icon is clicked, the view should be updated and the tr should also be updated
            self._vispy_widget.canvas.update()
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
        pass

    def on_mouse_release(self, event):
        pass

    def on_mouse_move(self, event):
        """
        Draw selection line along dragging mouse
        """
        if event.button == 1 and event.is_dragging and self.mode is not 'point':
            if self.mode is 'lasso':
                self.line_pos.append(event.pos)
                self.line.set_data(np.array(self.line_pos))
            else:
                width = event.pos[0] - self.selection_origin[0]
                height = event.pos[1] - self.selection_origin[1]
                center = (width / 2. + self.selection_origin[0], height / 2. + self.selection_origin[1], 0)

                if self.mode is 'rectangle':
                    self.line_pos = self.rectangle_vertice(center, height, width)
                    self.line.set_data(np.array(self.line_pos))

                if self.mode is 'ellipse':
                    # create a circle instead of ellipse here
                    self.line_pos = self.ellipse_vertice(center, radius=(np.abs((width + height) / 4.), np.abs((width + height) / 4.)),
                                                         start_angle=0., span_angle=360., num_segments=500)
                    self.line.set_data(pos=np.array(self.line_pos), connect='strip')
            self._vispy_widget.canvas.update()

    def get_visible_data(self):
        visible = []
        # Loop over visible layer artists
        for layer_artist in self._vispy_data_viewer._layer_artist_container:
            # Only extract Data objects, not subsets
            if isinstance(layer_artist.layer, Data):
                visible.append(layer_artist.layer)
        visual = layer_artist.visual  # we only have one visual for each canvas
        return visible, visual

    def mark_selected(self, mask, visible_data):
        # We now make a subset state. For scatter plots we'll want to use an
        # ElementSubsetState, while for cubes, we'll need to change to a
        # MaskSubsetState.
        subset_state = PatchedElementSubsetState(visible_data, np.where(mask)[0])

        # We now check what the selection mode is, and update the selection as
        # needed (this is delegated to the correct subset mode).
        mode = EditSubsetMode()
        focus = visible_data[0] if len(visible_data) > 0 else None
        mode.update(self._data_collection, subset_state, focus_data=focus)

    def lasso_reset(self):
        # Reset lasso
        self.line_pos = []
        self.line.set_data(np.zeros((0, 2)))
        self.line.update()
        self.selection_origin = (0, 0)
        self._vispy_widget.canvas.update()

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

    def ellipse_vertice(self, center, radius, start_angle, span_angle, num_segments):
        # Borrow from _generate_vertices in vispy/visual/ellipse.py

        if isinstance(radius, (list, tuple)):
            if len(radius) == 2:
                xr, yr = radius
            else:
                raise ValueError("radius must be float or 2 value tuple/list"
                                 " (got %s of length %d)" % (type(radius),
                                                             len(radius)))
        else:
            xr = yr = radius

        start_angle = np.deg2rad(start_angle)

        vertices = np.empty([num_segments + 2, 2], dtype=np.float32)  # Segment as 1000

        # split the total angle into num_segments intances
        theta = np.linspace(start_angle,
                            start_angle + np.deg2rad(span_angle),
                            num_segments + 1)

        # PolarProjection
        vertices[:-1, 0] = center[0] + xr * np.cos(theta)
        vertices[:-1, 1] = center[1] + yr * np.sin(theta)

        # close the curve
        vertices[num_segments + 1] = np.float32([center[0], center[1]])

        return vertices[:-1]
