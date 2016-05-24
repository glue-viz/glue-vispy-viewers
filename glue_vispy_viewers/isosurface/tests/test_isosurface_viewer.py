import numpy as np

from glue.core import Data
from glue.core.tests.util import simple_session

from ..isosurface_viewer import VispyIsosurfaceViewer


def test_Isosurface_viewer():

    # Create fake data
    data = Data(primary=np.arange(1000).reshape((10, 10, 10)))

    # Create fake session
    session = simple_session()
    session.data_collection.append(data)

    w = VispyIsosurfaceViewer(session)
    w.add_data(data)
    w.show()

    # TODO: add tests for visual options
