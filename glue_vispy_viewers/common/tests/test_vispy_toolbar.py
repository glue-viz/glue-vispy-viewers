# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

from __future__ import absolute_import, division, print_function

import warnings
from mock import patch

from .util import simple_session

from ..vispy_data_viewer import BaseVispyViewer

from .. import tools  # noqa:

# we need to test both toolbar and tool here
# solve the viewer test bug first

# similar to glue/viewers/common/qt/tests/test_toolbar.py


class ExampleViewer(BaseVispyViewer):

    def __init__(self, session, parent=None):

        super(ExampleViewer, self).__init__(session, parent=parent)

    def callback(self, mode):
        self._called_back = True


def test_toolbar(tmpdir):
    session = simple_session()
    with warnings.catch_warnings(record=True) as w:
        viewer = ExampleViewer(session)
        toolbar = viewer.toolbar

        # test save tool
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = tmpdir.join('test.png').strpath, 'jnk'
            toolbar.actions['vispy:save'].trigger()

        # test rotate tool
        toolbar.actions['vispy:rotate'].toggle()
        assert toolbar.active_tool.tool_id == 'vispy:rotate'
        # TODO: assert a mode here
        toolbar.actions['vispy:rotate'].toggle()
        assert toolbar.active_tool is None

        # test record tool
        try:
            import imageio  # noqa
            toolbar.actions['vispy:record'].toggle()
            assert toolbar.active_tool.tool_id == 'vispy:record'
            toolbar.actions['vispy:record'].toggle()
            assert toolbar.active_tool.tool_id is None
        except ImportError:
            print('Imageio package needed')

    assert len(w) == 0
