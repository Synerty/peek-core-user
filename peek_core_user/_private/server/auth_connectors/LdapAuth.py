import logging
from typing import List

from twisted.cred.error import LoginFailed
from twisted.internet.defer import inlineCallbacks
from vortex.VortexFactory import VortexFactory

from peek_core_user._private.agent.RpcForLogic import RpcForLogic
from peek_core_user._private.ldap_auth.ldap_auth import checkLdapAuth
from peek_core_user._private.ldap_auth.ldap_auth import (
    maybeCreateInternalUserBlocking,
)
from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.storage.Setting import LDAP_VERIFY_SSL
from peek_core_user._private.storage.Setting import globalSetting

__author__ = "synerty"

logger = logging.getLogger(__name__)

import ldap


class LdapNotEnabledError(Exception):
    pass


class LdapAuth(AuthABC):
    @inlineCallbacks
    def checkPassBlocking(
        self, dbSession, userName, password, forService, userUuid=None
    ):
        """Login User

        :param forService:
        :param dbSession:
        :param userName: The username of the user.
        :param password: The users secret password.
        :param userUuid: The decoded objectSid of the user from LDAP
        :rtype
        """

        assert forService in (1, 2, 3), "Unhandled for service type"

        ldapSettings: List[LdapSetting] = dbSession.query(LdapSetting).all()

        if not globalSetting(dbSession, LDAP_VERIFY_SSL):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        if not ldapSettings:
            raise Exception("LDAPAuth: No LDAP servers configured.")

        firstException = None

        for ldapSetting in ldapSettings:
            if forService == self.FOR_ADMIN:
                if not ldapSetting.adminEnabled:
                    continue

            elif forService == self.FOR_OFFICE:
                if not ldapSetting.desktopEnabled:
                    continue

            elif forService == self.FOR_FIELD:
                if not ldapSetting.mobileEnabled:
                    continue

            else:
                raise Exception(
                    "LDAPAuth: Unhandled forService type %s" % forService
                )

            if (
                "@" in userName
                and userName.split("@")[1] != ldapSetting.ldapDomain
            ):
                continue

            try:
                logger.info("Trying LDAP login for %s", ldapSetting.ldapDomain)

                if ldapSetting.agentHost is None:
                    logger.debug("Trying LDAP on Logic Service")
                    (groups, ldapLoggedInUser) = checkLdapAuth(
                        userName, password, ldapSetting, userUuid
                    )
                else:
                    logger.debug(
                        "Trying LDAP on Agent %s", ldapSetting.agentHost
                    )
                    (
                        groups,
                        ldapLoggedInUser,
                    ) = yield self.__forwardLdapAuthToAgent(
                        userName, password, ldapSetting, userUuid
                    )

                return groups, maybeCreateInternalUserBlocking(
                    dbSession, ldapLoggedInUser
                )
            except LoginFailed as e:
                if not firstException:
                    firstException = e

        logger.error("Login failed for %s, %s", userName, str(firstException))

        if firstException:
            raise firstException

        raise LoginFailed("LDAPAuth: No LDAP providers found for this service")

    @inlineCallbacks
    def __forwardLdapAuthToAgent(
        self, userName, password, ldapSetting, userUuid
    ):
        agentHost = ldapSetting.agentHost
        try:
            vortexUuid = VortexFactory.getRemoteVortexInfoByIp(agentHost)
        except KeyError:
            raise LoginFailed(
                "Could not find Peek Agent with hostname %s", agentHost
            )

        return (
            yield RpcForLogic.tryLdapLoginOnAgent.callForVortexUuid(
                vortexUuid, userName, password, ldapSetting, userUuid
            )
        )
