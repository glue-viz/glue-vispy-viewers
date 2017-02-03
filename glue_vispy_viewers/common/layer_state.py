from __future__ import absolute_import, division, print_function

from glue.external.echo import CallbackProperty
from glue.core.state_objects import State

__all__ = ['VispyLayerState']


class VispyLayerState(State):
    """
    A base state object for all Vispy layers
    """

    layer = CallbackProperty()
    visible = CallbackProperty(True)
    zorder = CallbackProperty(0)
