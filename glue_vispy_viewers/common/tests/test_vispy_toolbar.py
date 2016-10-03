# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

from __future__ import absolute_import, division, print_function

import warnings


from glue.icons.qt import get_icon
from glue.core.tests.util import simple_session

from ..vispy_widget import VispyWidget
from ..toolbar import VispyDataViewerToolbar
from ..new_toolbar import VispyViewerToolbar, SaveTool, RecordTool, RotateTool
from ..vispy_data_viewer import BaseVispyViewer

# we need to test both toolbar and tool here
# solve the viewer test bug first

# similar to glue/viewers/common/qt/tests/test_toolbar.py


class ExampleViewer(BaseVispyViewer):

    _toolbar_cls = VispyViewerToolbar

    def __init__(self, session, parent=None):
        super(ExampleViewer, self).__init__(session, parent=parent)
        v = VispyWidget(parent)

        self.central_widget = v
        self.setCentralWidget(self.central_widget)
        self.toolbar = self._toolbar_cls(vispy_widget=v, parent=self)

    '''def initialize_toolbar(self):  # difference with set_default_tool
        super(ExampleViewer, self).initialize_toolbar()
        tool = SaveTool(self)
        self.toolbar.add_tool(tool)

        rotate_tool = RotateTool(self)
        self.toolbar.add_tool(rotate_tool)

        try:
            import imageio
            tool2 = RecordTool(self)
            self.toolbar.add_tool(tool2)
        except ImportError:
            print('Install imageio first!')

        # assert 1==0'''

    def _update_attributes(self):
        pass

    def callback(self, mode):
        self._called_back = True


def test_toolbar():
    session = simple_session()
    with warnings.catch_warnings(record=True) as w:
        viewer = ExampleViewer(session)
        toolbar = viewer.toolbar

        # test save tool
        # toolbar.actions['Save'].trigger()  # TODO: add a proper test for dialogue test
        # assert toolbar.active_tool.tool_id == 'Save'

        # test rotate tool
        toolbar.actions['Rotate'].toggle()
        assert toolbar.active_tool.tool_id == 'Rotate'
        # TODO: assert a mode here
        toolbar.actions['Rotate'].toggle()
        assert toolbar.active_tool is None

        # test record tool
        # is record in actions.key
        # test record toggle too

    # assert len(w) == 1
