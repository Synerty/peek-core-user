import logging

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.server.api.UserAdminAuthApi import UserAdminAuthApi
from peek_core_user._private.server.api.UserHookApi import UserHookApi
from peek_core_user._private.server.api.UserImportApi import UserImportApi
from peek_core_user._private.server.api.UserInfoApi import UserInfoApi
from peek_core_user._private.server.api.UserLoginApi import UserLoginApi
from peek_core_user._private.server.controller.AdminAuthController import \
    AdminAuthController
from peek_core_user._private.server.controller.ImportController import \
    ImportController
from peek_core_user._private.server.controller.LoginLogoutController import \
    LoginLogoutController
from peek_core_user.server.UserApiABC import UserApiABC

logger = logging.getLogger(__name__)


class UserApi(UserApiABC):

    def __init__(self, deviceApi: DeviceApiABC,
                 dbSessionCreator,
                 importController: ImportController,
                 loginLogoutController: LoginLogoutController,
                 adminAuthController: AdminAuthController):
        self._hookApi = UserHookApi()

        self._importApi = UserImportApi(importController=importController)

        self._infoApi = UserInfoApi(deviceApi=deviceApi,
                                    dbSessionCreator=dbSessionCreator)

        self._loginApi = UserLoginApi(loginLogoutController=loginLogoutController)

        self._adminAuthApi = UserAdminAuthApi(adminAuthController=adminAuthController)

    def shutdown(self):
        self._loginApi.shutdown()
        self._importApi.shutdown()
        self._hookApi.shutdown()
        self._infoApi.shutdown()
        self._adminAuthApi.shutdown()

        self._loginApi = None
        self._importApi = None
        self._hookApi = None
        self._infoApi = None
        self._adminAuthApi = None

    @property
    def loginApi(self) -> UserLoginApi:
        return self._loginApi

    @property
    def importApi(self) -> UserImportApi:
        return self._importApi

    @property
    def hookApi(self) -> UserHookApi:
        return self._hookApi

    @property
    def infoApi(self) -> UserInfoApi:
        return self._infoApi

    @property
    def adminAuth(self) -> UserAdminAuthApi:
        return self._adminAuthApi
