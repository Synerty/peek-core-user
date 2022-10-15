import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Tuple

from sqlalchemy.orm.exc import NoResultFound
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_core_user._private.storage.InternalUserPassword import (
    InternalUserPassword,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)


class AuthABC(metaclass=ABCMeta):
    FOR_ADMIN = 1
    FOR_OFFICE = 2
    FOR_FIELD = 3

    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @abstractmethod
    def checkPassAsync(
        self, userName: str, password: str, forService: int
    ) -> Tuple[List[str], InternalUserTuple]:
        raise NotImplementedError()

    @deferToThreadWrapWithLogger(logger)
    def getInternalUser(
        self, userName, raiseNotLoggedInException=True
    ) -> Optional[InternalUserTuple]:

        session = self._dbSessionCreator()
        try:
            authenticatedUsers = (
                session.query(InternalUserTuple)
                .filter(InternalUserTuple.userName == userName)
                .all()
            )
            session.expunge_all()

            if len(authenticatedUsers) == 0:
                if raiseNotLoggedInException:
                    raise NoResultFound()
                else:
                    return None

            if len(authenticatedUsers) != 1:
                if raiseNotLoggedInException:
                    raise Exception("Too many users found")
                else:
                    return None

            return authenticatedUsers[0]

            # No commit needed, we only query
        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def getInternalUserAndPassword(self, userName):

        session = self._dbSessionCreator()
        try:
            authenticatedUserPasswords = (
                session.query(InternalUserTuple, InternalUserPassword)
                .join(
                    InternalUserPassword, isouter=True
                )  # effectively `LEFT JOIN`
                .filter(InternalUserTuple.userName == userName)
                .all()
            )
            session.expunge_all()

            if len(authenticatedUserPasswords) == 0:
                raise NoResultFound()

            if len(authenticatedUserPasswords) != 1:
                raise Exception("Too many users found")

            return authenticatedUserPasswords[0]

            # No commit needed, we only query
        finally:
            session.close()
