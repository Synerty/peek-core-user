import {addTupleType, Tuple} from "@synerty/vortexjs";
import {userTuplePrefix} from "../_private/PluginNames";

@addTupleType
export class UserListItemTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserListItemTuple";

    constructor() {
        super(UserListItemTuple.tupleName); // Matches server side
    }

    userId: string;
    displayName: string;

    get userName(): string {
        return this.userId;
    }

    get userTitle(): string {
        return this.displayName;
    }
}
