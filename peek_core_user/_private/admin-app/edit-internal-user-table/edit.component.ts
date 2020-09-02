import {Component, NgZone} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    extend,
    TupleActionPushService,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService
} from "@synerty/vortexjs";
import {userFilt} from "@peek/peek_core_user/_private";
import {InternalUserTuple} from "../tuples/InternalUserTuple";
import {InternalUserUpdatePasswordAction} from "../tuples/InternalUserUpdatePasswordAction";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js"
import {GroupDetailTuple} from "@peek/peek_core_user/tuples/GroupDetailTuple";


@Component({
    selector: 'pl-user-edit-internal-user',
    templateUrl: './edit.component.html'
})
export class EditInternalUserComponent extends ComponentLifecycleEventEmitter {
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        "key": "admin.Edit.InternalUserTuple"
    };

    items: InternalUserTuple[] = [];
    itemsToDelete: InternalUserTuple[] = [];

    loader: TupleLoader;

    groupsById: {} = {};
    groups = [];

    likeTitle: string = '';

    constructor(private balloonMsg: BalloonMsgService,
                private actionProcessor: TupleActionPushService,
                private tupleObserver: TupleDataObserverService,
                private zone:NgZone,
                vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this, () => {
            return extend({likeTitle: this.likeTitle}, this.filt, userFilt);
        });

        this.loader.observable
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: InternalUserTuple[]) => {
                this.items = tuples;
                this.itemsToDelete = [];
            });

        this.tupleObserver
            .subscribeToTupleSelector(new TupleSelector(GroupDetailTuple.tupleName, {}))
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: GroupDetailTuple[]) => {
                this.groups = tuples;
                this.groupsById = {};
                for (let tuple of tuples) {
                    this.groupsById[tuple.id] = tuple;
                }
            });

    }

    needFilter(): boolean {
        return this.likeTitle == null || this.likeTitle.length < 3;
    }

    haveItems(): boolean {
        return this.items != null && this.items.length != 0;
    }

    load() {
        if (this.needFilter()) {
            this.items = [];
            this.itemsToDelete = [];
            return;
        }

        this.loader.load();
    }

    addRow() {
        let t = new InternalUserTuple();
        // Add any values needed for this list here, EG, for a lookup list you might add:
        // t.lookupName = this.lookupName;
        this.items.push(t);
    }

    removeRow(item: InternalUserTuple) {
        if (item.id != null)
            this.itemsToDelete.push(item);

        let index: number = this.items.indexOf(item);
        if (index !== -1) {
            this.items.splice(index, 1);
        }
    }

    setPassword(item: InternalUserTuple) {
        let action = new InternalUserUpdatePasswordAction();
        action.userId = item.id;
        action.newPassword = prompt("Please enter a new password");

        if (action.newPassword == null || action.newPassword.length == 0) {
            return;
        }

        this.actionProcessor.pushAction(action)
            .then(() => this.balloonMsg.showSuccess("Password updated successfully"))
            .catch(e => this.balloonMsg.showError(e));
    }

    save() {
        let itemsToDelete = this.itemsToDelete;

        this.loader.save(this.items)
            .then(() => {
                if (itemsToDelete.length != 0) {
                    return this.loader.del(itemsToDelete);
                }
            })
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch(e => this.balloonMsg.showError(e));
    }
    groupTitleForId(id:number):string {
        return this.groupsById[id].groupTitle;
    }

    addGroupRow(user: InternalUserTuple) {
        user.groupIds.push(null);
    }

    removeGroupRow(user: InternalUserTuple, index: number) {
        console.log(`Removing ${index}`);
        user.groupIds.splice(index, 1);

    }

    updateGroup(user: InternalUserTuple, index:number, id: string) {
        user.groupIds[index] = parseInt(id);
    }

}
