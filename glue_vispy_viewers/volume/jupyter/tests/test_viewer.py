import numpy as np
from glue.core import Data
from glue_jupyter import jglue
from ..volume_viewer import JupyterVispyVolumeViewer


def test_jupyter_volume_basic():
    app = jglue()
    data = Data(x=np.arange(24).reshape((2, 3, 4)), label="cube data")
    app.add_data(data)
    app.new_data_viewer(JupyterVispyVolumeViewer, data=data)


def test_jupyter_volume_scatter_overlay():
    app = jglue()
    data1 = Data(x=np.arange(24).reshape((2, 3, 4)), label="cube data")
    data2 = Data(x=[1, 2, 3], y=[1, 2, 3], z=[2, 3, 4], label="tabular data")
    app.add_data(data1)
    app.add_data(data2)
    viewer = app.new_data_viewer(JupyterVispyVolumeViewer, data=data1)
    viewer.add_data(data2)
