# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

from __future__ import absolute_import, division, print_function

import os
import pytest
from mock import patch

from glue.core.tests.util import simple_session

from ..vispy_data_viewer import BaseVispyViewer

from .. import tools  # noqa:

try:
    import imageio  # noqa
except ImportError:
    IMAGEIO_INSTALLED = False
else:
    IMAGEIO_INSTALLED = True


class ExampleViewer(BaseVispyViewer):

    def __init__(self, session, parent=None):

        super(ExampleViewer, self).__init__(session, parent=parent)

    def callback(self, mode):
        self._called_back = True


class TestToolbar(object):

    def setup_method(self):
        self.session = simple_session()
        self.viewer = ExampleViewer(self.session)
        self.toolbar = self.viewer.toolbar

    def teardown_method(self):
        self.session = None
        self.viewer.close()
        self.viewer = None
        self.toolbar = None

    def test_save(self, tmpdir, capsys):

        self.viewer.show()

        filename = tmpdir.join('test.png').strpath

        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = filename, 'png'
            self.toolbar.actions['vispy:save'].trigger()

        assert os.path.exists(filename)

        out, err = capsys.readouterr()
        assert out.strip() == ""
        assert err.strip() == ""

    def test_rotate(self, capsys):

        self.toolbar.actions['vispy:rotate'].toggle()
        assert self.toolbar.active_tool.tool_id == 'vispy:rotate'

        self.toolbar.actions['vispy:rotate'].toggle()
        assert self.toolbar.active_tool is None

        out, err = capsys.readouterr()
        assert out.strip() == ""
        assert err.strip() == ""

    @pytest.mark.skipif('not IMAGEIO_INSTALLED')
    def test_record(self, tmpdir, capsys):

        filename = tmpdir.join('test.gif').strpath

        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = filename, 'gif'
            self.toolbar.actions['vispy:record'].toggle()

        assert self.toolbar.active_tool.tool_id == 'vispy:record'

        self.toolbar.actions['vispy:record'].toggle()
        assert self.toolbar.active_tool is None

        assert os.path.exists(filename)

        out, err = capsys.readouterr()
        assert out.strip() == ""
        assert err.strip() == ""
