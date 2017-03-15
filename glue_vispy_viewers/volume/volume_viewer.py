from __future__ import absolute_import, division, print_function

from glue.core.state import lookup_class_with_patches
from glue.config import settings
from glue.core import message as msg

from qtpy.QtWidgets import QMessageBox

from ..common.vispy_data_viewer import BaseVispyViewer
from .layer_artist import VolumeLayerArtist
from .layer_style_widget import VolumeLayerStyleWidget

from ..scatter.layer_artist import ScatterLayerArtist
from ..scatter.layer_style_widget import ScatterLayerStyleWidget

from ..common import tools  # noqa
from ..common import selection_tools  # noqa
from . import volume_toolbar  # noqa

try:
    import OpenGL  # flake8: noqa
except ImportError:
    OPENGL_INSTALLED = False
else:
    OPENGL_INSTALLED = True


class VispyVolumeViewer(BaseVispyViewer):

    LABEL = "3D Volume Rendering"

    _layer_style_widget_cls = {VolumeLayerArtist: VolumeLayerStyleWidget,
                               ScatterLayerArtist: ScatterLayerStyleWidget}

    tools = BaseVispyViewer.tools + ['vispy:lasso', 'vispy:rectangle',
                                     'vispy:circle', 'volume3d:point']

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

        if data.ndim == 1:

            if len(self._layer_artist_container) == 0:
                QMessageBox.critical(self, "Error",
                                     "Can only add a scatter plot overlay once a volume is present".format(data.ndim),
                                     buttons=QMessageBox.Ok)

            # Assume that the user wants a scatter plot overlay

            layer_artist = ScatterLayerArtist(layer=data, vispy_viewer=self)
            self._vispy_widget._update_limits()

        elif data.ndim == 3:

            if len(self._layer_artist_container) > 0:
                required_shape = self._layer_artist_container[0].shape
                if data.shape != required_shape:
                    QMessageBox.critical(self, "Error",
                                         "Shape of dataset ({0}) does not agree "
                                         "with shape of existing datasets in volume "
                                         "rendering ({1})".format(data.shape, required_shape),
                                         buttons=QMessageBox.Ok)
                    return False

            layer_artist = VolumeLayerArtist(layer=data, vispy_viewer=self)

        else:

            QMessageBox.critical(self, "Error",
                                 "Data should be 1- or 3-dimensional ({0} dimensions found)".format(data.ndim),
                                 buttons=QMessageBox.Ok)
            return False

        if len(self._layer_artist_container) == 0:
            self.state.set_limits(*layer_artist.bbox)

        self._layer_artist_container.append(layer_artist)

        for subset in data.subsets:
            self.add_subset(subset)

        return True

    def add_subset(self, subset):

        if subset in self._layer_artist_container:
            return

        if subset.ndim == 1:
            layer_artist = ScatterLayerArtist(layer=subset, vispy_viewer=self)
        elif subset.ndim == 3:
            layer_artist = VolumeLayerArtist(layer=subset, vispy_viewer=self)
        else:
            return

        self._layer_artist_container.append(layer_artist)

    def _add_subset(self, message):
        self.add_subset(message.subset)

    @classmethod
    def __setgluestate__(cls, rec, context):
        viewer = super(VispyVolumeViewer, cls).__setgluestate__(rec, context)
        return viewer

    def _update_appearance_from_settings(self, message):
        super(VispyVolumeViewer, self)._update_appearance_from_settings(message)
        if hasattr(self._vispy_widget, '_multivol'):
            self._vispy_widget._multivol.set_background(settings.BACKGROUND_COLOR)
