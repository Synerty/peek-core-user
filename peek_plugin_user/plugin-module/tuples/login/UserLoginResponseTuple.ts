import {addTupleType, Tuple} from "@synerty/vortexjs";
import {userTuplePrefix} from "../../_private/PluginNames";
import {UserDetailTuple} from "../UserDetailTuple";


@addTupleType
export class UserLoginResponseTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserLoginResponseTuple";

    constructor() {
        super(UserLoginResponseTuple.tupleName); // Matches server side
    }

    userName: string;
    userToken: string;
    deviceToken: string;
    deviceDescription: string;
    vehicleId: string = '';

    userDetail: UserDetailTuple;

    succeeded: boolean = true;

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logon
    // continues.
    acceptedWarningKeys: string[] = [];

    // A dict of warnings from a failed logon action.
    // key = a unique key for this warning
    // value = the description of the warning for the user
    warnings: {} = {};
    errors: string[] = [];

}