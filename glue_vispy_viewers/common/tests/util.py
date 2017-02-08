from mock import MagicMock
from glue.core.tests.util import simple_session as _simple_session


def simple_session():
    session = _simple_session()
    session.application._mode_toolbar = MagicMock()
    session.application._mode_toolbar.isHidden = MagicMock()
    session.application._mode_toolbar.isHidden.return_value = False
    return session
