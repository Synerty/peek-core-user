import logging

from twisted.cred.error import LoginFailed
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.server.controller.PasswordUpdateController import (
    PasswordUpdateController,
)
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserGroupTuple import (
    InternalUserGroupTuple,
)
from peek_core_user._private.storage.Setting import ADMIN_LOGIN_GROUP
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_ADMIN,
)
from peek_core_user._private.storage.Setting import MOBILE_LOGIN_GROUP
from peek_core_user._private.storage.Setting import OFFICE_LOGIN_GROUP
from peek_core_user._private.storage.Setting import globalSetting
from peek_core_user.server.UserDbErrors import UserNotFoundException
from peek_core_user.server.UserDbErrors import UserPasswordNotSetException
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)

logger = logging.getLogger(__name__)


class InternalAuth(AuthABC):
    @inlineCallbacks
    def checkPassAsync(self, userName, password, forService):
        authenticatedUserPassword = yield self.getInternalUserAndPassword(
            userName
        )

        # if user not found
        if (
            not authenticatedUserPassword
            or not authenticatedUserPassword.InternalUserTuple
        ):
            raise UserNotFoundException(userName)

        # if user found but user is created by LDAP
        if (
            authenticatedUserPassword.InternalUserTuple.authenticationTarget
            == UserAuthTargetEnum.LDAP
        ):
            # delegate to LDAPAuth
            return (
                yield LdapAuth(self._dbSessionCreator).checkPassAsync(
                    userName, password, forService
                )
            )

        if not authenticatedUserPassword.InternalUserPassword:
            raise UserPasswordNotSetException(userName)

        #     def checkPassAsync(self, userName, password, forService):
        #
        # Check if the user is actually logged into this device.
        return (
            yield self._checkInternalPass(
                authenticatedUserPassword, password, forService
            )
        )

    @deferToThreadWrapWithLogger(logger)
    def _checkInternalPass(self, authenticatedUser, password, forService):

        dbSession = self._dbSessionCreator()
        try:

            passObj = authenticatedUser.InternalUserPassword
            if passObj.password != PasswordUpdateController.hashPass(password):
                raise LoginFailed(
                    "Peek InternalAuth: Username or password is incorrect"
                )

            groups = (
                dbSession.query(InternalGroupTuple)
                .join(InternalUserGroupTuple)
                .filter(InternalUserGroupTuple.userId == passObj.userId)
                .all()
            )

            groupNames = [g.groupName for g in groups]

            if forService == self.FOR_ADMIN:
                adminGroup = globalSetting(dbSession, ADMIN_LOGIN_GROUP)
                if adminGroup not in set(groupNames):
                    raise LoginFailed(
                        "Peek InternalAuth:"
                        " User is not a member of an authorised group"
                    )

            elif forService == self.FOR_OFFICE:
                officeGroup = globalSetting(dbSession, OFFICE_LOGIN_GROUP)
                if officeGroup not in set(groupNames):
                    raise LoginFailed(
                        "Peek InternalAuth:"
                        " User is not a member of an authorised group"
                    )

            elif forService == self.FOR_FIELD:
                fieldGroup = globalSetting(dbSession, MOBILE_LOGIN_GROUP)
                if fieldGroup not in set(groupNames):
                    raise LoginFailed(
                        "Peek InternalAuth:"
                        " User is not a member of an authorised group"
                    )

            else:
                raise Exception(
                    "Peek InternalAuth: Unhandled forService type %s"
                    % forService
                )

            # No commit needed, we only query

            return groupNames, authenticatedUser.InternalUserTuple

        finally:
            dbSession.close()

    @deferToThreadWrapWithLogger(logger)
    def isInternalAuthEnabled(self):
        session = self._dbSessionCreator()
        try:
            return globalSetting(session, INTERNAL_AUTH_ENABLED_FOR_ADMIN)
            # No commit needed, we only query

        finally:
            session.close()
