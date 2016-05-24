from glue.core.state import lookup_class_with_patches
from glue.external.qt.QtGui import QMessageBox

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget
from .volume_toolbar import VolumeSelectionToolbar

try:
    import OpenGL  # flake8: noqa
except ImportError:
    OPENGL_INSTALLED = False
else:
    OPENGL_INSTALLED = True


class VispyVolumeViewer(BaseVispyViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = VolumeLayerStyleWidget
    _toolbar_cls = VolumeSelectionToolbar

    def __init__(self, *args, **kwargs):
        super(VispyVolumeViewer, self).__init__(*args, **kwargs)
        if not OPENGL_INSTALLED:
            self.close()
            QMessageBox.critical(self, "Error",
                                 "The PyOpenGL package is required for the "
                                 "3D volume rendering viewer",
                                 buttons=QMessageBox.Ok)

    def add_data(self, data):

        if data in self._layer_artist_container:
            return True

        if data.ndim != 3:
            QMessageBox.critical(self, "Error",
                                 "Data should be 3-dimensional ({0} dimensions found)".format(data.ndim),
                                 buttons=QMessageBox.Ok)
            return False

        if len(self._layer_artist_container) > 0:
            required_shape = self._layer_artist_container[0].shape
            if data.shape != required_shape:
                QMessageBox.critical(self, "Error",
                                     "Shape of dataset ({0}) does not agree "
                                     "with shape of existing datasets in volume "
                                     "rendering ({1})".format(data.shape, required_shape),
                                     buttons=QMessageBox.Ok)
                return False

        layer_artist = VolumeLayerArtist(data, vispy_viewer=self)

        if len(self._layer_artist_container) == 0:
            self._options_widget.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        return True

    def add_subset(self, subset):
        if subset in self._layer_artist_container:
            return

        if subset.to_mask().ndim != 3:
            return

        layer_artist = VolumeLayerArtist(subset, vispy_viewer=self)
        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_attributes(self, index=None, layer_artist=None):
        pass

    @classmethod
    def __setgluestate__(cls, rec, context):
        viewer = super(VispyVolumeViewer, cls).__setgluestate__(rec, context)
        viewer._update_attributes()
        return viewer

    def restore_layers(self, layers, context):
        for l in layers:
            cls = lookup_class_with_patches(l.pop('_type'))
            props = dict((k, context.object(v)) for k, v in l.items())
            layer_artist = cls(props['layer'], vispy_viewer=self)
            if len(self._layer_artist_container) == 0:
                self._options_widget.set_limits(*layer_artist.bbox)
            self._layer_artist_container.append(layer_artist)
            layer_artist.set(**props)
