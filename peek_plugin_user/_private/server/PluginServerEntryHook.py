import logging

from celery import Celery

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_plugin_user._private.server.ClientTupleActionProcessor import \
    makeTupleActionProcessorHandler
from peek_plugin_user._private.server.ClientTupleDataObservable import \
    makeTupleDataObservableHandler
from peek_plugin_user._private.server.admin_backend import makeAdminBackendHandlers
from peek_plugin_user._private.server.api.UserApi import UserApi
from peek_plugin_user._private.server.controller.ImportController import \
    ImportController
from peek_plugin_user._private.server.controller.MainController import MainController
from peek_plugin_user.server.UserApiABC import UserApiABC

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC,
                            PluginServerWorkerEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)
        self._userApi = None

        self._handlers = []

    def load(self) -> None:
        from peek_plugin_user._private.tuples import loadPrivateTuples
        loadPrivateTuples()

        from peek_plugin_user._private.storage.DeclarativeBase import loadStorageTuples
        loadStorageTuples()

        from peek_plugin_user.tuples import loadPublicTuples
        loadPublicTuples()

        logger.debug("loaded")

    def start(self):
        deviceApi: DeviceApiABC = self.platform.getOtherPluginApi("peek_core_device")

        importController = ImportController()
        self._handlers.append(importController)

        self._userApi = UserApi(deviceApi,
                                self.dbSessionCreator,
                                importController)

        mainController = MainController(self.dbSessionCreator, self._userApi)
        self._handlers.append(mainController)

        tupleObservable = makeTupleDataObservableHandler(
                self.dbSessionCreator, self._userApi
        )
        self._handlers.append(tupleObservable)

        self._userApi.setTupleObserver(tupleObservable)
        importController.setTupleObserver(tupleObservable)

        self._handlers.append(makeTupleActionProcessorHandler(mainController))

        # Add the backend handlers
        self._handlers.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        logger.debug("started")

    def stop(self):
        for handler in self._handlers:
            handler.shutdown()

        self._userApi.shutdown()

        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    @property
    def publishedServerApi(self) -> UserApiABC:
        return self._userApi

    @property
    def dbMetadata(self):
        from peek_plugin_user._private.storage import DeclarativeBase
        return DeclarativeBase.metadata

    ###### Implement PluginServerWorkerEntryHookABC

    @property
    def celeryApp(self) -> Celery:
        from peek_plugin_user._private.worker.CeleryApp import celeryApp
        return celeryApp
