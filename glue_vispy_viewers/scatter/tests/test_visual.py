import numpy as np

from glue.core import Data
from glue.core.application_base import Application

from ...tests.helpers import set_canvas_size, visual_test
from ..scatter_viewer import SimpleVispyScatterViewer


@visual_test(tolerance=5)
def test_visual_scatter3d():

    np.random.seed(12345)
    n = 500
    data = Data(
        x=np.random.normal(0, 1, n),
        y=np.random.normal(0, 1, n),
        z=np.random.normal(0, 1, n),
        label='cloud',
    )

    app = Application()
    app.data_collection.append(data)
    viewer = app.new_data_viewer(SimpleVispyScatterViewer, data=data)

    set_canvas_size(viewer, 500, 500)
    viewer.state.x_min, viewer.state.x_max = -3, 3
    viewer.state.y_min, viewer.state.y_max = -3, 3
    viewer.state.z_min, viewer.state.z_max = -3, 3
    viewer.state.layers[0].color = 'crimson'
    viewer.state.layers[0].size = 4

    return viewer
