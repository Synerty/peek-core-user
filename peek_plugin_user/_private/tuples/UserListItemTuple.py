import logging

from peek_plugin_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class UserListItemTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserListItemTuple"

    userId = TupleField(comment="The unique ID of the user", typingType=str)
    displayName = TupleField(comment="The nice name of the user", typingType=str)
