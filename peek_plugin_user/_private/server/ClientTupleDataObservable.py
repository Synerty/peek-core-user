import logging

from peek_plugin_user._private.PluginNames import userPluginFilt, \
    userPluginObservableName
from peek_plugin_user._private.server.tuple_providers.GroupDetailTupleProvider import \
    GroupDetailTupleProvider
from peek_plugin_user._private.server.tuple_providers.UserLoggedInTupleProvider import \
    UserLoggedInTupleProvider
from peek_plugin_user.tuples.UserListItemTuple import \
    UserListItemTuple
from peek_plugin_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_plugin_user.tuples.GroupDetailTuple import GroupDetailTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler, \
    TuplesProviderABC
from .tuple_providers.UserListItemTupleProvider import UserListItemTupleProvider

logger = logging.getLogger(__name__)


class Dummy(TuplesProviderABC):
    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, *args):
        return Payload(filt, tuples=[]).makePayloadEnvelope().toVortexMsg()


def makeTupleDataObservableHandler(dbSessionCreator, ourApi):
    obserable = TupleDataObservableHandler(observableName=userPluginObservableName,
                                           additionalFilt=userPluginFilt)

    obserable.addTupleProvider(GroupDetailTuple.tupleName(),
                               GroupDetailTupleProvider(ourApi))

    obserable.addTupleProvider(UserListItemTuple.tupleName(),
                               UserListItemTupleProvider(dbSessionCreator, ourApi))

    obserable.addTupleProvider(UserLoggedInTuple.tupleType(),
                               UserLoggedInTupleProvider(dbSessionCreator, ourApi))

    return obserable
