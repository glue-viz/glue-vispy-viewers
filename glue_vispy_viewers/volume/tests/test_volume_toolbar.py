
from distutils.version import LooseVersion

import numpy as np

import glue
from glue.core import DataCollection, Data
from glue.app.qt.application import GlueApplication
from glue.core.component import Component
from glue.core.tests.util import simple_session

from ..volume_viewer import VispyVolumeViewer

GLUE_LT_08 = LooseVersion(glue.__version__) < LooseVersion('0.8')


def make_test_data():

    data = Data(label="Test Cube Data")

    np.random.seed(12345)

    for letter in 'abc':
        comp = Component(np.random.random((10, 10, 10)))
        data.add_component(comp, letter)

    return data



def test_volumeviewer_toolbar():
    session = simple_session()
    v = VispyVolumeViewer(session)
    data = make_test_data()
    v.add_data(data)
    assert v.toolbar is not None