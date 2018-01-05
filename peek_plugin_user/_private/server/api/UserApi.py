import logging

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_plugin_user._private.server.api.UserHookApi import UserHookApi
from peek_plugin_user._private.server.api.UserImportApi import UserImportApi
from peek_plugin_user._private.server.api.UserInfoApi import UserInfoApi
from peek_plugin_user._private.server.api.UserLoginApi import UserLoginApi
from peek_plugin_user._private.server.controller.ImportController import \
    ImportController
from peek_plugin_user.server.UserApiABC import UserApiABC
from peek_plugin_user.server.UserHookApiABC import UserHookApiABC
from peek_plugin_user.server.UserImportApiABC import UserImportApiABC
from peek_plugin_user.server.UserInfoApiABC import UserInfoApiABC
from peek_plugin_user.server.UserLoginApiABC import UserLoginApiABC

logger = logging.getLogger(__name__)


class UserApi(UserApiABC):

    def __init__(self, deviceApi: DeviceApiABC,
                 dbSessionCreator,
                 importController:ImportController):

        self._hookApi = UserHookApi()

        self._importApi = UserImportApi(importController=importController)

        self._infoApi = UserInfoApi(deviceApi=deviceApi,
                                    dbSessionCreator=dbSessionCreator)

        self._loginApi = UserLoginApi(deviceApi=deviceApi,
                                      dbSessionCreator=dbSessionCreator,
                                      hookApi=self._hookApi,
                                      infoApi=self._infoApi)

    def setTupleObserver(self, tupleObservable):
        self._loginApi.setTupleObserver(tupleObservable)

    def shutdown(self):
        self._loginApi.shutdown()
        self._importApi.shutdown()
        self._hookApi.shutdown()
        self._infoApi.shutdown()

        self._loginApi = None
        self._importApi = None
        self._hookApi = None
        self._infoApi = None


    @property
    def loginApi(self) -> UserLoginApiABC:
        return self._loginApi

    @property
    def importApi(self) -> UserImportApiABC:
        return self._importApi

    @property
    def hookApi(self) -> UserHookApiABC:
        return self._hookApi

    @property
    def infoApi(self) -> UserInfoApiABC:
        return self._infoApi