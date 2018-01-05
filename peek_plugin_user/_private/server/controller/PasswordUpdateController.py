import logging

import hashlib
from twisted.internet.defer import Deferred

from peek_plugin_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_plugin_user._private.tuples.InternalUserUpdatePasswordAction import \
    InternalUserUpdatePasswordAction
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC

logger = logging.getLogger(__name__)


# This is the CRUD handler
class PasswordUpdateController(TupleActionProcessorDelegateABC):
    def __init__(self, ormSessionCreator):
        self.ormSessionCreator = ormSessionCreator

    @staticmethod
    def hashPass(rawPass: str):
        m = hashlib.sha1()
        m.update(b'peek is a secure thingie')
        m.update(rawPass.encode())
        return m.hexdigest()

    @deferToThreadWrapWithLogger(logger)
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        """ Process Tuple Action

        The method generates the vortexMsg for the vortex to send.
s
        :param tupleAction: The C{TupleAction} to process.

        """

        assert isinstance(tupleAction, InternalUserUpdatePasswordAction), (
            "not isinstance(tupleAction, InternalUserUpdatePasswordAction)")

        ormSession = self.ormSessionCreator()
        try:
            user = (
                ormSession
                    .query(InternalUserTuple)
                    .filter(InternalUserTuple.id == tupleAction.userId)
                    .one()
            )

            user.password = self.hashPass(tupleAction.newPassword)

            ormSession.commit()

        finally:
            ormSession.close()
