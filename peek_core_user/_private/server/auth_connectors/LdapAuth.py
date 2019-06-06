import logging
from typing import List

from twisted.cred.error import LoginFailed

__author__ = 'synerty'

logger = logging.getLogger(__name__)

import ldap


class LdapNotEnabledError(Exception):
    pass


class LdapAuth:

    def checkPassBlocking(self, dbSession, userName, password) -> List[str]:
        """ Login User

        :param dbSession:
        :param userName: The username of the user.
        :param password: The users secret password.
        :rtype
        """
        (ldapDoamin, ldapOuFolders, ldapCnFolders, ldapUri) = self._loadLdapSettings(
            dbSession
        )

        try:

            conn = ldap.initialize(ldapUri)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # make the connection
            conn.simple_bind_s('%s@%s' % (userName, ldapDoamin), password)
            ldapFilter = "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))" % userName

            dcParts = ','.join(['DC=%s' % part for part in ldapDoamin.split('.')])

            ldapBases = self._makeLdapBase(ldapOuFolders, userName, "OU")
            ldapBases += self._makeLdapBase(ldapCnFolders, userName, "CN")

            for ldapBase in ldapBases:
                ldapBase = "%s,%s" % (ldapBase, dcParts)

                try:
                    # Example Base : 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                    userDetails = conn.search_st(ldapBase, ldap.SCOPE_SUBTREE,
                                                 ldapFilter, None, 0, 10)

                    if userDetails:
                        break

                except ldap.NO_SUCH_OBJECT:
                    raise

        except ldap.NO_SUCH_OBJECT:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        except ldap.INVALID_CREDENTIALS:
            logger.error("Login failed for %s, invalid credentials", userName)
            raise LoginFailed("Username or password is incorrect")

        if not userDetails:
            logger.error("Login failed for %s, failed to query LDAP for user groups",
                         userName)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        userDetails = userDetails[0][1]

        groups = []
        for memberOf in userDetails['memberOf']:
            group = memberOf.decode().split(',')[0]
            if '=' in group:
                group = group.split('=')[1]
            groups.append(group)

        return groups

    def _loadLdapSettings(self, dbSession):

        from peek_core_user._private.storage.Setting import ldapSetting, \
            LDAP_DOMAIN_NAME, LDAP_URI, LDAP_CN_FOLDERS, \
            LDAP_OU_FOLDERS

        try:
            ldapSettings = ldapSetting(dbSession)

            ldapDoamin = ldapSettings[LDAP_DOMAIN_NAME]
            ldapCnFolders = ldapSettings[LDAP_CN_FOLDERS]
            ldapOuFolders = ldapSettings[LDAP_OU_FOLDERS]
            ldapUri = ldapSettings[LDAP_URI]

        except Exception as e:
            logger.error("Failed to query for LDAP connection settings")
            logger.exception(e)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")

        return ldapDoamin, ldapOuFolders, ldapCnFolders, ldapUri

    def _makeLdapBase(self, ldapFolders, userName, propertyName):
        try:
            ldapBases = []
            for folder in ldapFolders.split(','):
                folder = folder.strip()
                if not folder:
                    continue

                parts = []
                for part in folder.split('/'):
                    part = part.strip()
                    if not part:
                        continue
                    parts.append('%s=%s' % (propertyName, part))

                ldapBases.append(','.join(reversed(parts)))

            return ldapBases

        except Exception as e:
            logger.error(
                "Login failed for %s, failed to parse LDAP %s Folders setting" % propertyName,
                userName)

            logger.exception(e)

            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs")
