import {Tuple} from "@synerty/vortexjs";
import {userTuplePrefix} from "../_private/PluginNames";

export class GroupDetailTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "GroupDetailTuple";

    constructor() {
        super(GroupDetailTuple.tupleName); // Matches server side
    }

    // ID
    id: number;

    //  The name of the group, EG C917
    groupName: string;

    //  The title of the group, EG 'Chief Wiggum'
    groupTitle: string;

}
