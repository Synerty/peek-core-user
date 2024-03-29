import logging
from collections import namedtuple
from datetime import datetime
from typing import List
from typing import Tuple

import pytz
from peek_core_device.server.DeviceApiABC import DeviceApiABC

from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_ADMIN,
)
from twisted.cred.error import LoginFailed
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_user._private.server.api.UserFieldHookApi import UserFieldHookApi
from peek_core_user._private.server.api.UserInfoApi import UserInfoApi
from peek_core_user._private.server.auth_connectors.InternalAuth import (
    InternalAuth,
)
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_FIELD,
)
from peek_core_user._private.storage.Setting import (
    INTERNAL_AUTH_ENABLED_FOR_OFFICE,
)
from peek_core_user._private.storage.Setting import LDAP_AUTH_ENABLED
from peek_core_user._private.storage.Setting import globalSetting
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_core_user._private.tuples.LoggedInUserStatusTuple import (
    LoggedInUserStatusTuple,
)
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_core_user.server.UserDbErrors import (
    UserIsNotLoggedInToThisDeviceError,
)
from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLoginResponseTuple import (
    UserLoginResponseTuple,
)
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from peek_core_user.tuples.login.UserLogoutResponseTuple import (
    UserLogoutResponseTuple,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)

USER_ALREADY_LOGGED_ON_KEY = "pl-user.USER_ALREADY_LOGGED_ON"
DEVICE_ALREADY_LOGGED_ON_KEY = "pl-user.DEVICE_ALREADY_LOGGED_ON_KEY"

_AuthSettings = namedtuple(
    "_AuthSettings",
    [
        "internalFieldEnabled",
        "internalOfficeEnabled",
        "internalAdminEnabled",
        "ldapAuthEnabled",
    ],
)


class _ForceLogout:
    def __init__(self, userUuid, deviceToken):
        self._userUuid = userUuid
        self._deviceToken = deviceToken

    def forceDbLogout(self, ormSession):
        ormSession.query(UserLoggedIn).filter(
            UserLoggedIn.userUuid == self._userUuid
        ).filter(UserLoggedIn.deviceToken == self._deviceToken).delete(
            synchronize_session=False
        )

    def notify(self, clientTupleObservable):
        clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=self._deviceToken),
            )
        )


class LoginLogoutController:
    def __init__(
        self, deviceApi: DeviceApiABC, dbSessionCreator: DbSessionCreator
    ):
        self._deviceApi: DeviceApiABC = deviceApi
        self._fieldServiceHookApi: UserFieldHookApi = None
        self._infoApi: UserInfoApi = None
        self._dbSessionCreator: DbSessionCreator = dbSessionCreator
        self._clientTupleObservable: TupleDataObservableHandler = None
        self._adminTupleObservable: TupleDataObservableHandler = None

    def setup(
        self,
        clientTupleObservable,
        adminTupleObservable,
        hookApi: UserFieldHookApi,
        infoApi: UserInfoApi,
    ):
        self._clientTupleObservable = clientTupleObservable
        self._adminTupleObservable = adminTupleObservable
        self._fieldServiceHookApi = hookApi
        self._infoApi = infoApi

    def shutdown(self):
        self._clientTupleObservable = None
        self._fieldServiceHookApi = None
        self._infoApi = None

    @inlineCallbacks
    def _checkPassAsync(
        self, userName, password, isFieldService: bool, userUuid=None
    ) -> Tuple[List[str], InternalUserTuple]:
        if not password:
            raise LoginFailed("Password is empty")

        # TODO Make the client tell us if it's for office or field

        lastException = None

        forService = AuthABC.FOR_OFFICE
        if isFieldService:
            forService = AuthABC.FOR_FIELD

        authSettings = yield self._getAuthsEnabled()

        # TRY INTERNAL IF ITS ENABLED
        try:
            internalAuth = InternalAuth(self._dbSessionCreator)
            if (
                forService == AuthABC.FOR_FIELD
                and authSettings.internalFieldEnabled
            ):
                return (
                    yield internalAuth.checkPassAsync(
                        userName, password, forService
                    )
                )

            if (
                forService == AuthABC.FOR_OFFICE
                and authSettings.internalOfficeEnabled
            ):
                return (
                    yield internalAuth.checkPassAsync(
                        userName, password, forService
                    )
                )

        except Exception as e:
            lastException = e

        # TRY LDAP IF ITS ENABLED
        try:
            ldapAuth = LdapAuth(self._dbSessionCreator)
            if authSettings.ldapAuthEnabled:
                return (
                    yield ldapAuth.checkPassAsync(
                        userName, password, forService, userUuid
                    )
                )

        except Exception as e:
            lastException = e

        if lastException:
            raise lastException

        raise Exception(
            "No authentication handlers are enabled, enable one in settings"
        )

    @deferToThreadWrapWithLogger(logger)
    def _logoutInDb(
        self, logoutTuple: UserLogoutAction, raiseNotLoggedInException=True
    ):
        """
        Returns Deferred[UserLogoutResponseTuple]
        """

        session = self._dbSessionCreator()
        try:
            # Check if the user is actually logged into this device.
            qry = (
                session.query(UserLoggedIn)
                .filter(UserLoggedIn.userName == logoutTuple.userName)
                .filter(UserLoggedIn.deviceToken == logoutTuple.deviceToken)
            )

            if qry.count() == 0:
                if raiseNotLoggedInException:
                    raise UserIsNotLoggedInToThisDeviceError(
                        logoutTuple.userName
                    )
                else:
                    return

            session.delete(qry.one())
            session.commit()

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _getAuthsEnabled(self) -> _AuthSettings:
        """
        Returns Deferred[UserLogoutResponseTuple]
        """

        session = self._dbSessionCreator()
        try:
            settings = globalSetting(session)
            return _AuthSettings(
                internalFieldEnabled=settings[INTERNAL_AUTH_ENABLED_FOR_FIELD],
                internalOfficeEnabled=settings[
                    INTERNAL_AUTH_ENABLED_FOR_OFFICE
                ],
                internalAdminEnabled=settings[INTERNAL_AUTH_ENABLED_FOR_ADMIN],
                ldapAuthEnabled=settings[LDAP_AUTH_ENABLED],
            )

        finally:
            session.close()

    @inlineCallbacks
    def logout(self, logoutTuple: UserLogoutAction) -> Deferred:
        """Logout

        :param logoutTuple: The tuple containing the information to process
                                for the logout.

        :return A deferred that fires with List[UserLogoutResponseTuple]
        """

        deviceDescription = yield self._deviceApi.deviceDescription(
            logoutTuple.deviceToken
        )

        response = UserLogoutResponseTuple(
            userName=logoutTuple.userName,
            deviceToken=logoutTuple.deviceToken,
            deviceDescription=deviceDescription,
            acceptedWarningKeys=logoutTuple.acceptedWarningKeys,
            succeeded=True,
        )

        if logoutTuple.isFieldService:
            # Give the hooks a chance to fail the logout
            yield self._fieldServiceHookApi.callLogoutHooks(response)

        # If there are no problems, proceed with the logout.
        try:
            if response.succeeded:
                yield self._logoutInDb(logoutTuple)

        finally:
            # Delay this, otherwise the user gets kicked off before getting
            # the nice success message
            reactor.callLater(
                0.05, self._sendLogoutUpdate, logoutTuple.deviceToken
            )

        self._adminTupleObservable.notifyOfTupleUpdateForTuple(
            LoggedInUserStatusTuple.tupleType()
        )

        return response

    def _sendLogoutUpdate(self, deviceToken: str):
        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=deviceToken),
            )
        )

    @inlineCallbacks
    def _loginInDb(self, loginTuple: UserLoginAction):
        blockMultipleLogins = loginTuple.isFieldService

        userDetail = yield self._infoApi.user(loginTuple.userName)

        # This will login from the internal user if one already exists or
        # login from LDAP and create a user if an internal does not exist
        groups, _ = yield self._checkPassAsync(
            loginTuple.userName,
            loginTuple.password,
            blockMultipleLogins,
            userDetail.userUuid if userDetail else None,
        )
        return (yield self._loginInDbInThread(loginTuple, groups))

    @deferToThreadWrapWithLogger(logger)
    def _loginInDbInThread(self, loginTuple: UserLoginAction, groups):
        """
        Returns Deferred[UserLoginResponseTuple]

        """

        userName = loginTuple.userName
        acceptedWarningKeys = set(loginTuple.acceptedWarningKeys)
        deviceToken = loginTuple.deviceToken
        vehicle = loginTuple.vehicleId
        isFieldService = loginTuple.isFieldService
        blockMultipleLogins = isFieldService

        forceLogouter = None

        responseTuple = UserLoginResponseTuple(
            userName=userName,
            userToken="Not implemented",
            succeeded=False,
            acceptedWarningKeys=loginTuple.acceptedWarningKeys,
            vehicleId=loginTuple.vehicleId,
        )

        if not deviceToken:
            raise Exception("peekToken must be supplied")

        thisDeviceDescription = self._deviceApi.deviceDescriptionBlocking(
            deviceToken
        )

        userDetail = self._infoApi.userBlocking(userName)

        # check user group and user password
        ormSession = self._dbSessionCreator()
        try:
            if not userDetail:
                responseTuple.setFailed()
                return responseTuple

            userKey = userDetail.userKey
            userUuid = userDetail.userUuid
            loginTuple.userName = userDetail.userName
            responseTuple.userName = userDetail.userName
            responseTuple.userDetail = userDetail

            # Find any current login sessions
            userLoggedIn = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.userUuid == userUuid)
                .filter(UserLoggedIn.isFieldLogin == isFieldService)
                .all()
            )
            userLoggedIn = userLoggedIn[0] if userLoggedIn else None

            loggedInElsewhere = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.deviceToken != deviceToken)
                .filter(UserLoggedIn.userUuid == userUuid)
                .filter(UserLoggedIn.isFieldLogin == isFieldService)
                .all()
            )

            if blockMultipleLogins and len(loggedInElsewhere) not in (0, 1):
                raise Exception(
                    "Found more than 1 ClientDevice for"
                    + (" token %s" % deviceToken)
                )

            loggedInElsewhere = (
                loggedInElsewhere[0] if loggedInElsewhere else None
            )

            sameDevice = userLoggedIn and loggedInElsewhere is None

            # If the user is logged in, but not to this client device, raise exception
            if blockMultipleLogins and userLoggedIn and not sameDevice:
                if USER_ALREADY_LOGGED_ON_KEY in acceptedWarningKeys:
                    forceLogouter = _ForceLogout(
                        userUuid, loggedInElsewhere.deviceToken
                    )

                    forceLogouter.forceDbLogout(ormSession)

                    userLoggedIn = False

                else:
                    otherDeviceDescription = (
                        self._deviceApi.deviceDescriptionBlocking(
                            loggedInElsewhere.deviceToken
                        )
                    )

                    # This is false if the logged in device has been removed from
                    # enrollment
                    if otherDeviceDescription:
                        responseTuple.setFailed()
                        responseTuple.addWarning(
                            USER_ALREADY_LOGGED_ON_KEY,
                            "User %s is already logged in, on device %s"
                            % (userName, otherDeviceDescription),
                        )

                        return responseTuple

                    # Else, The old device has been deleted,
                    # Just let them login to the same device.

                    forceLogouter = _ForceLogout(
                        loggedInElsewhere.userUuid,
                        loggedInElsewhere.deviceToken,
                    )
                    forceLogouter.forceDbLogout(ormSession)

            # If we're logging into the same device, but already logged in
            if sameDevice:  # Logging into the same device
                sameDeviceDescription = (
                    self._deviceApi.deviceDescriptionBlocking(
                        userLoggedIn.deviceToken
                    )
                )

                responseTuple.deviceToken = userLoggedIn.deviceToken
                responseTuple.deviceDescription = sameDeviceDescription
                responseTuple.succeeded = True
                return responseTuple

            anotherUserOnThatDevice = (
                ormSession.query(UserLoggedIn)
                .filter(UserLoggedIn.deviceToken == deviceToken)
                .filter(UserLoggedIn.userUuid != userUuid)
                .all()
            )

            if anotherUserOnThatDevice:
                anotherUserOnThatDevice = anotherUserOnThatDevice[0]
                if DEVICE_ALREADY_LOGGED_ON_KEY in acceptedWarningKeys:
                    forceLogouter = _ForceLogout(
                        anotherUserOnThatDevice.userUuid,
                        anotherUserOnThatDevice.deviceToken,
                    )
                    forceLogouter.forceDbLogout(ormSession)

                else:
                    responseTuple.setFailed()
                    responseTuple.addWarning(
                        DEVICE_ALREADY_LOGGED_ON_KEY,
                        "User %s is currently logged into this device : %s"
                        % (
                            anotherUserOnThatDevice.userName,
                            thisDeviceDescription,
                        ),
                    )

                    return responseTuple

            # Create the user logged in entry

            newUser = UserLoggedIn(
                userName=userName.lower(),
                userKey=userKey.lower(),
                userUuid=userUuid,
                loggedInDateTime=datetime.now(pytz.utc),
                deviceToken=deviceToken,
                vehicle=vehicle,
                isFieldLogin=isFieldService,
            )
            ormSession.add(newUser)
            ormSession.commit()

            # Respond with a successful login
            responseTuple.deviceToken = deviceToken
            responseTuple.deviceDescription = thisDeviceDescription
            responseTuple.succeeded = True
            return responseTuple

        finally:
            ormSession.close()

            if forceLogouter:
                forceLogouter.notify(self._clientTupleObservable)

    @inlineCallbacks
    def login(self, loginTuple: UserLoginAction):
        """
        Returns Deferred[UserLoginResponseTuple]

        """
        loginResponse = None
        try:
            loginResponse = yield self._loginInDb(loginTuple)

            if loginTuple.isFieldService:
                yield self._fieldServiceHookApi.callLoginHooks(loginResponse)

        # except UserAlreadyLoggedInError as e:
        #     pass
        #
        # except DeviceAlreadyLoggedInError as e:
        #     pass
        #
        # except UserIsNotLoggedInToThisDeviceError as e:
        #     pass

        except Exception as e:
            # Log the user out again if the hooks fail
            logoutTuple = UserLogoutAction(
                userName=loginTuple.userName, deviceToken=loginTuple.deviceToken
            )

            # Force logout, we don't care if it works or not.
            try:
                yield self._logoutInDb(
                    logoutTuple, raiseNotLoggedInException=False
                )
            except UserIsNotLoggedInToThisDeviceError:
                pass

            logger.debug(f"User login failed: {e}")
            raise e

        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=loginTuple.deviceToken),
            )
        )

        self._adminTupleObservable.notifyOfTupleUpdateForTuple(
            LoggedInUserStatusTuple.tupleType()
        )

        return loginResponse

    def _forceLogout(self, ormSession, userUuid, deviceToken):
        ormSession.query(UserLoggedIn).filter(
            UserLoggedIn.userUuid == userUuid
        ).filter(UserLoggedIn.deviceToken == deviceToken).delete(
            synchronize_session=False
        )

        self._clientTupleObservable.notifyOfTupleUpdate(
            TupleSelector(
                UserLoggedInTuple.tupleType(),
                selector=dict(deviceToken=deviceToken),
            )
        )
