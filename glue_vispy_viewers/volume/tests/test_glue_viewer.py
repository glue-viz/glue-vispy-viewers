import operator
import numpy as np
from glue.external.qt import get_qapp
from glue.core.data import Data
from glue.core.data_collection import DataCollection

try:
    from glue.app.qt.application import GlueApplication
except:
    from glue.qt.glue_application import GlueApplication

from glue.core.subset import InequalitySubsetState
# from glue.core.tests.util import simple_session
from ..vol_glue_viewer import GlueVispyViewer


def test_viewer():

    app = get_qapp()

    data = Data(x=np.arange(1000).reshape((10, 10, 10)) / 1000.)
    dc = DataCollection([data])
    app = GlueApplication(dc)
    app.new_data_viewer(GlueVispyViewer, data=data)
    subset_state1 = InequalitySubsetState(data.find_component_id('x'), 2/3., operator.gt)
    dc.new_subset_group(label='test_subset1', subset_state=subset_state1)
    subset_state2 = InequalitySubsetState(data.find_component_id('x'), 1/3., operator.lt)
    dc.new_subset_group(label='test_subset2', subset_state=subset_state2)
    app.show()
