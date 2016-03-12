import numpy as np

from glue.core import Data
from glue.core.tests.util import simple_session

from ..volume_viewer import VispyVolumeViewer


def test_volume_viewer():

    # Create fake data
    data = Data(primary=np.arange(1000).reshape((10,10,10)))

    # Create fake session
    session = simple_session()
    session.data_collection.append(data)

    w = VispyVolumeViewer(session)
    w.add_data(data)
    w.show()

    # TODO: add tests for visual options
