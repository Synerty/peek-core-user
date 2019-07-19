import logging

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_user._private.server.api.UserApi import UserApi
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class UserLoggedInTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator,
                 ourApi: UserApi):
        self._dbSessionCreator = dbSessionCreator
        self._ourApi = ourApi

        from peek_core_user.server.UserApiABC import UserApiABC
        assert isinstance(self._ourApi, UserApiABC), (
            "We didn't get a UserApiABC")

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        userName = tupleSelector.selector["userName"]

        deviceTokens = yield self._ourApi.infoApi.peekDeviceTokensForUser(userName)

        tuples = [
            UserLoggedInTuple(userName=userName, deviceToken=dt)
            for dt in deviceTokens
        ]

        payload = Payload(filt=filt, tuples=tuples)
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
