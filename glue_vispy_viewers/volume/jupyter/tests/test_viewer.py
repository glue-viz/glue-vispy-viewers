import numpy as np
from glue.core import Data
from glue_jupyter import jglue
from ..volume_viewer import JupyterVispyVolumeViewer


def test_basic_jupyter_volume():
    app = jglue()
    data = Data(x=np.arange(24).reshape((2, 3, 4)), label="cube data")
    app.add_data(data)
    app.new_data_viewer(JupyterVispyVolumeViewer, data=data)
