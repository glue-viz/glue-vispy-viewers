# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

import os
import sys
import pytest
from unittest.mock import patch

from glue_qt.app import GlueApplication
from glue.core import Data

from ....scatter.qt.scatter_viewer import VispyScatterViewer

from ... import tools  # noqa:

try:
    import imageio  # noqa
except ImportError:
    IMAGEIO_INSTALLED = False
else:
    IMAGEIO_INSTALLED = True

IS_WIN = sys.platform == 'win32'
PY_LT_37 = sys.version_info[:2] < (3, 7)


@pytest.mark.skipif('PY_LT_37 or IS_WIN')
@pytest.mark.skipif('not IS_WIN', reason='Teardown disaster')
def test_save(tmpdir, capsys):

    app = GlueApplication()
    app.show()

    viewer = app.new_data_viewer(VispyScatterViewer)
    data = Data(x=[1, 2, 3], label='Data')
    app.data_collection.append(data)
    viewer.add_data(data)

    filename = tmpdir.join('test.png').strpath

    with patch('qtpy.compat.getsavefilename') as fd:
        fd.return_value = filename, 'png'
        viewer.toolbar.tools['save'].subtools[0].activate()

    assert os.path.exists(filename)

    out, err = capsys.readouterr()
    assert out.strip() == ""
    assert err.strip() == ""

    app.close()


@pytest.mark.skipif('not IS_WIN', reason='Teardown disaster')
def test_rotate(capsys):

    app = GlueApplication()
    viewer = app.new_data_viewer(VispyScatterViewer)

    viewer.toolbar.actions['vispy:rotate'].toggle()
    assert viewer.toolbar.active_tool.tool_id == 'vispy:rotate'

    viewer.toolbar.actions['vispy:rotate'].toggle()
    assert viewer.toolbar.active_tool is None

    out, err = capsys.readouterr()
    assert out.strip() == ""
    assert err.strip() == ""

    app.close()


@pytest.mark.skip(reason='Teardown disaster')
def test_reset(tmpdir, capsys):

    app = GlueApplication()
    viewer = app.new_data_viewer(VispyScatterViewer)
    data = Data(x=[1, 2, 3], label='Data')
    app.data_collection.append(data)
    app.show()
    viewer.add_data(data)

    assert viewer.state.x_min == 1.
    assert viewer.state.y_min == 1.
    assert viewer.state.z_min == 1.

    assert viewer.state.x_max == 3.
    assert viewer.state.y_max == 3.
    assert viewer.state.z_max == 3.

    viewer.state.x_min = 2
    viewer.state.y_min = 3
    viewer.state.z_min = 5

    viewer.state.x_max = 6
    viewer.state.y_max = 7
    viewer.state.z_max = 8

    viewer.toolbar.actions['vispy:reset'].trigger()

    assert viewer.state.x_min == 1.
    assert viewer.state.y_min == 1.
    assert viewer.state.z_min == 1.

    assert viewer.state.x_max == 3.
    assert viewer.state.y_max == 3.
    assert viewer.state.z_max == 3.

    out, err = capsys.readouterr()
    assert out.strip() == ""
    with pytest.skip(reason='Transient "I/O operation on closed file" errors'):
        assert err.strip() == ""

    app.close()


@pytest.mark.skipif('not IMAGEIO_INSTALLED')
@pytest.mark.skipif('not IS_WIN', reason='Teardown disaster')
def test_record(tmpdir, capsys):

    app = GlueApplication()
    viewer = app.new_data_viewer(VispyScatterViewer)

    filename = tmpdir.join('test.gif').strpath

    with patch('qtpy.compat.getsavefilename') as fd:
        fd.return_value = filename, 'gif'
        viewer.toolbar.actions['vispy:record'].toggle()

    assert viewer.toolbar.active_tool.tool_id == 'vispy:record'

    viewer.toolbar.actions['vispy:record'].toggle()
    assert viewer.toolbar.active_tool is None

    assert os.path.exists(filename)

    out, err = capsys.readouterr()
    assert out.strip() == ""
    with pytest.raises(AssertionError, match=r'I/O operation on closed file'):
        assert err.strip() == ""

    app.close()
