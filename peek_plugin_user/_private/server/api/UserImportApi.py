import logging

from twisted.internet.defer import Deferred

from peek_plugin_user._private.server.controller.ImportController import \
    ImportController
from peek_plugin_user.server.UserImportApiABC import UserImportApiABC

logger = logging.getLogger(__name__)


class UserImportApi(UserImportApiABC):
    def __init__(self, importController: ImportController):
        self._importController = importController

    def shutdown(self):
        pass

    def importInternalUsers(self, importHash: str, usersVortexMsg: bytes) -> Deferred:
        return self._importController.importInternalUsers(importHash, usersVortexMsg)

    def importInternalGroups(self, importHash: str, groupsVortexMsg: bytes) -> Deferred:
        return self._importController.importInternalGroups(importHash, groupsVortexMsg)
