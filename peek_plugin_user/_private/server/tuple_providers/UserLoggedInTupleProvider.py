import logging

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_user._private.server.api.UserApi import UserApi
from peek_plugin_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class UserLoggedInTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator,
                 ourApi: UserApi):
        self._dbSessionCreator = dbSessionCreator
        self._ourApi = ourApi

        from peek_plugin_user.server.UserApiABC import UserApiABC
        assert isinstance(self._ourApi, UserApiABC), (
            "We didn't get a UserApiABC")

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        userName = tupleSelector.selector["userName"]

        deviceToken = yield self._ourApi.infoApi.peekDeviceTokenForUser(userName)

        tuple_ = UserLoggedInTuple(userName=userName, deviceToken=deviceToken)

        payloadEnvelope = yield Payload(filt=filt, tuples=[tuple_]).toEncodedPayloadDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
