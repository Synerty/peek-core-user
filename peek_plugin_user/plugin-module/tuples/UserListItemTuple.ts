import {Tuple} from "@synerty/vortexjs";
import {userTuplePrefix} from "../_private/PluginNames";

export class UserListItemTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserListItemTuple";

    constructor() {
        super(UserListItemTuple.tupleName); // Matches server side
    }

    userId: string;
    displayName: string;
}
