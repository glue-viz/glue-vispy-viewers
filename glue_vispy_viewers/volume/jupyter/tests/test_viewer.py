import numpy as np
from glue.core import Data
from glue_jupyter import jglue
from ..volume_viewer import JupyterVispyVolumeViewer
from ....scatter.jupyter.layer_state_widget import Scatter3DLayerStateWidget
from ..layer_state_widget import Volume3DLayerStateWidget


def test_basic_jupyter_volume():
    app = jglue()
    data = Data(x=np.arange(24).reshape((2, 3, 4)), label="cube data")
    app.add_data(data)
    viewer = app.new_data_viewer(JupyterVispyVolumeViewer, data=data)
    viewer.cleanup()


def test_jupyter_layer_widgets():
    app = jglue()
    volume_data = Data(x=np.arange(24).reshape((2, 3, 4)), label="cube data")
    scatter_data = Data(x=np.arange(0, 5), y=np.arange(5, 10), z=np.arange(20, 25))
    for index, component in enumerate(("x", "y", "z")):
        app.add_link(volume_data, f"Pixel Axis {2-index} [{component}]", scatter_data, component)
    app.add_data(volume_data)
    app.add_data(scatter_data)
    viewer = app.new_data_viewer(JupyterVispyVolumeViewer, data=volume_data)
    viewer.add_data(scatter_data)

    layer_options = viewer.layer_options
    volume_layer = viewer.layers[0]
    scatter_layer = viewer.layers[1]
    volume_widget = layer_options.layer_to_dict(volume_layer, 0)["layer_panel"]
    assert isinstance(volume_widget, Volume3DLayerStateWidget)
    scatter_widget = layer_options.layer_to_dict(scatter_layer, 1)["layer_panel"]
    assert isinstance(scatter_widget, Scatter3DLayerStateWidget)

    viewer.cleanup()
