from mock import MagicMock
from glue.core.tests.util import simple_session as _simple_session


def simple_session():
    session = _simple_session()
    return session
