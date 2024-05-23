# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

import numpy as np
import pytest
import sys
from unittest.mock import patch

from glue.core import Data, DataCollection
from glue_qt.app import GlueApplication

from glue.core.tests.util import simple_session

from ..data_viewer import BaseVispyViewer
from ....volume.qt.volume_viewer import VispyVolumeViewer
from ....scatter.qt.scatter_viewer import VispyScatterViewer

IS_WIN = sys.platform == 'win32'


def setup_function(func):
    import os
    os.environ['GLUE_TESTING'] = 'True'


class BaseTestDataViewer(object):
    ndim = 3

    def test_unregister_on_close(self):
        session = simple_session()
        hub = session.hub

        w = self.widget_cls(session)
        w.register_to_hub(hub)
        with patch.object(BaseVispyViewer, 'unregister') as unregister:
            w.close()
        unregister.assert_called_once_with(hub)

    @pytest.mark.skipif('IS_WIN', reason='Windows fatal exception: access violation')
    def test_add_viewer(self, tmpdir):

        d1 = Data(x=np.random.random((2,) * self.ndim))
        d2 = Data(x=np.random.random((2,) * self.ndim))
        dc = DataCollection([d1, d2])
        app = GlueApplication(dc)
        w = app.new_data_viewer(self.widget_cls, data=d1)
        w.viewer_size = (300, 400)

        filename = tmpdir.join('session.glu').strpath
        app.save_session(filename, include_data=True)

        app2 = GlueApplication.restore_session(filename)

        # test session is restored correctly
        for viewer in app2.viewers:
            assert viewer[0].viewer_size == (300, 400)

        app.close()
        app2.close()

    def test_options_widget(self):

        d1 = Data(x=np.random.random((2,) * self.ndim))
        d2 = Data(x=np.random.random((2,) * self.ndim))
        dc = DataCollection([d1, d2])
        app = GlueApplication(dc)
        w = app.new_data_viewer(self.widget_cls, data=d1)

        w.state.x_stretch = 0.5
        w.state.y_stretch = 1.0
        w.state.z_stretch = 2.0

        w.state.x_min = -0.1
        w.state.x_max = 10.1
        w.state.y_min = 0.1
        w.state.y_max = 10.9
        w.state.z_min = 0.2
        w.state.z_max = 10.8

        w.state.visible_axes = False

        app.close()


class TestDataViewerVolume(BaseTestDataViewer):
    widget_cls = VispyVolumeViewer


class TestDataViewerScatter(BaseTestDataViewer):
    widget_cls = VispyScatterViewer
