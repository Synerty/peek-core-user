import {addTupleType, Tuple} from "@synerty/vortexjs";
import {userTuplePrefix} from "@peek/peek_core_user/_private/PluginNames";


@addTupleType
export class UserLogoutResponseTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserLogoutResponseTuple";

    constructor() {
        super(UserLogoutResponseTuple.tupleName); // Matches server side
    }

    userName: string;
    deviceToken: string;
    deviceDescription: string;

    succeeded: boolean = true;

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logoff
    // continues.
    acceptedWarningKeys: string[] = [];

    // A dict of warnings from a failed logoff action.
    // key = a unique key for this warning
    // value = the description of the warning for the user
    warnings: {} = {};
    errors: string[] = [];
}