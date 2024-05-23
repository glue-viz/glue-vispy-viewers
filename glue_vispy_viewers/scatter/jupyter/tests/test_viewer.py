from glue.core import Data
from glue_jupyter import jglue
from ..scatter_viewer import JupyterVispyScatterViewer


def test_basic_jupyter_scatter3d():
    app = jglue()
    data = Data(x=[1, 2, 3], y=[2, 3, 4], z=[5, 6, 7], label="xyz data")
    app.add_data(data)
    app.new_data_viewer(JupyterVispyScatterViewer, data=data)
