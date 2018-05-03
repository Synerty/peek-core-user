import logging
import uuid

from sqlalchemy.orm import subqueryload

from peek_plugin_user._private.PluginNames import userPluginFilt
from peek_plugin_user._private.server.controller.PasswordUpdateController import \
    PasswordUpdateController
from peek_plugin_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_plugin_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_plugin_user._private.tuples.UserListItemTuple import UserListItemTuple
from peek_plugin_user.tuples.UserDetailTuple import UserDetailTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.InternalUserTuple"}
filtKey.update(userPluginFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        likeTitle = payloadFilt["likeTitle"]

        tuples = []

        if likeTitle and len(likeTitle) >= 3:
            tuples = (
                session.query(InternalUserTuple)
                    .options(subqueryload(InternalUserTuple.groups))
                    .filter(InternalUserTuple.userTitle.ilike('%' + likeTitle + '%'))
                    .all()
            )

        for tuple in tuples:
            tuple.groupIds = []
            for group in tuple.groups:
                tuple.groupIds.append(group.id)

        return tuples

    def _create(self, session, payloadFilt):
        tuples = self.createDeclarative(session, payloadFilt)
        self._ext.afterCreate(tuples, session, payloadFilt)
        return Payload(tuples=tuples).makePayloadEnvelope()


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """ Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def _afterCommit(self, tuple_, tuples, session, payloadFilt):
        selector = {}
        # Copy any filter values into the selector
        selector["likeTitle"] = payloadFilt["likeTitle"]
        tupleSelector = TupleSelector(InternalUserTuple.tupleName(), selector)
        self._tupleDataObserver.notifyOfTupleUpdate(tupleSelector)

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(UserDetailTuple.tupleName(), {})
        )

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(UserListItemTuple.tupleName(), {})
        )

        for tuple in tuples:
            tuple.groupIds = []
            for group in tuple.groups:
                tuple.groupIds.append(group.id)

        return True

    afterUpdateCommit = _afterCommit
    afterDeleteCommit = _afterCommit

    def beforeUpdate(self, tuple_, tuples, session, payloadFilt):
        """ Before Update

        Set the password if it's saved with out a password

        """
        for tuple in tuples:
            if tuple.id is None and not tuple.password:
                tuple.password = PasswordUpdateController.hashPass(str(uuid.uuid4()))

        return True

    def middleUpdate(self, tuple_, tuples, session, payloadFilt):
        groupsById = {g.id: g for g in session.query(InternalGroupTuple)}

        for user in tuples:
            if user.groupIds:
                user.groups = [groupsById[gid] for gid in user.groupIds]

        return True



# This method creates an instance of the handler class.
def makeInternalUserTableHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, InternalUserTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(InternalUserTuple, __ExtUpdateObservable(tupleObservable))
    return handler
