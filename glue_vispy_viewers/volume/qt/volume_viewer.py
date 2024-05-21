from glue.core.data import BaseData
from glue.core.link_helpers import LinkSame

from qtpy.QtWidgets import QMessageBox
from qtpy.QtCore import QTimer

from ...common.qt.data_viewer import BaseVispyViewer
from .layer_style_widget import VolumeLayerStyleWidget

from ..volume_viewer import VispyVolumeViewerMixin

from ..layer_artist import VolumeLayerArtist
from ..layer_state import VolumeLayerState

from ...scatter.layer_artist import ScatterLayerArtist
from ...scatter.qt.layer_style_widget import ScatterLayerStyleWidget


class VispyVolumeViewer(VispyVolumeViewerMixin, BaseVispyViewer):

    _layer_style_widget_cls = {VolumeLayerArtist: VolumeLayerStyleWidget,
                               ScatterLayerArtist: ScatterLayerStyleWidget}

    def __init__(self, *args, **kwargs):

        super(VispyVolumeViewer, self).__init__(*args, **kwargs)

        # We now make it so that is the user clicks to drag or uses the
        # mouse wheel (or scroll on a trackpad), we downsample the volume
        # rendering temporarily.

        canvas = self._vispy_widget.canvas

        canvas.events.mouse_press.connect(self.mouse_press)
        canvas.events.mouse_wheel.connect(self.mouse_wheel)
        canvas.events.mouse_release.connect(self.mouse_release)

        viewbox = self._vispy_widget.view.camera.viewbox

        viewbox.events.mouse_wheel.connect(self.camera_mouse_wheel)
        viewbox.events.mouse_move.connect(self.camera_mouse_move)
        viewbox.events.mouse_press.connect(self.camera_mouse_press)
        viewbox.events.mouse_release.connect(self.camera_mouse_release)

        self._downsampled = False

        # For the mouse wheel, we receive discrete events so we need to have
        # a buffer (for now 250ms) before which we consider the mouse wheel
        # event to have stopped.

        self._downsample_timer = QTimer()
        self._downsample_timer.setInterval(250)
        self._downsample_timer.setSingleShot(True)
        self._downsample_timer.timeout.connect(self.mouse_release)

    def mouse_press(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol') and not self._downsampled:
                self._vispy_widget._multivol.downsample()
                self._downsampled = True

    def mouse_release(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol') and self._downsampled:
                self._vispy_widget._multivol.upsample()
                self._downsampled = False
                self._vispy_widget.canvas.render()

        self._update_slice_transform()
        self._update_clip()

    def mouse_wheel(self, event=None):
        if self.state.downsample:
            if hasattr(self._vispy_widget, '_multivol'):
                if not self._downsampled:
                    self.mouse_press()
        self._downsample_timer.start()
        if event is not None:
            event.handled = True

    def resizeEvent(self, event=None):
        self.mouse_wheel()
        super(VispyVolumeViewer, self).resizeEvent(event)

    # TODO: check if need to call QMessageBox.critical on errors in add_data
    # and _warn_no_free_volume_layers

    @classmethod
    def __setgluestate__(cls, rec, context):

        viewer = super(VispyVolumeViewer, cls).__setgluestate__(rec, context)

        if rec.get('_protocol', 0) < 2:

            # Find all data objects in layers (not subsets)
            layer_data = [layer.layer for layer in viewer.state.layers
                          if (isinstance(layer, VolumeLayerState) and
                              isinstance(layer.layer, BaseData))]

            if len(layer_data) > 1:
                reference = layer_data[0]
                for data in layer_data[1:]:
                    if data not in reference.pixel_aligned_data:
                        break
                else:
                    return viewer

            buttons = QMessageBox.Yes | QMessageBox.No
            message = ("The 3D volume rendering viewer now requires datasets to "
                       "be linked in order to be shown at the same time. Are you "
                       "happy for glue to automatically link your datasets by "
                       "pixel coordinates?")

            answer = QMessageBox.question(None, "Link data?", message,
                                          buttons=buttons,
                                          defaultButton=QMessageBox.Yes)

            if answer == QMessageBox.Yes:
                for data in layer_data[1:]:
                    if data not in reference.pixel_aligned_data:
                        for i in range(3):
                            link = LinkSame(reference.pixel_component_ids[i],
                                            data.pixel_component_ids[i])
                            viewer.session.data_collection.add_link(link)

        return viewer

    def __gluestate__(self, context):
        state = super(VispyVolumeViewer, self).__gluestate__(context)
        state['_protocol'] = 2
        return state
