// user.service.ts
import {Injectable} from "@angular/core";
import {Router} from "@angular/router";

import {Observable} from "rxjs/Observable";
import {Subject} from "rxjs/Subject";
import {
    addTupleType,
    ComponentLifecycleEventEmitter,
    Tuple,
    TupleSelector
} from "@synerty/vortexjs";
import {Ng2BalloonMsgService, UsrMsgLevel, UsrMsgType} from "@synerty/ng2-balloon-msg";
import {UserListItemTuple} from "../tuples/UserListItemTuple";
import {DeviceEnrolmentService} from "@peek/peek_core_device";
import {userTuplePrefix} from "../_private/PluginNames";
import {UserLoggedInTuple} from "../_private";
import {UserLogoutAction} from "../tuples/login/UserLogoutAction";
import {UserLogoutResponseTuple} from "../tuples/login/UserLogoutResponseTuple";
import {UserLoginAction} from "../tuples/login/UserLoginAction";
import {UserLoginResponseTuple} from "../tuples/login/UserLoginResponseTuple";
import {UserTupleService} from "../_private/user-tuple.service";


@addTupleType
export class UserServiceStateTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserServiceStateTuple";

    userDetails: UserListItemTuple;
    authToken: string;

    constructor() {
        super(UserServiceStateTuple.tupleName)
    }
}


@Injectable()
export class UserService extends ComponentLifecycleEventEmitter {

    private _loggedInStatus: Subject<boolean> = new Subject<boolean>();

    private _users: UserListItemTuple[] = [];
    private _userDisplayNameById: {};


    private state: UserServiceStateTuple = new UserServiceStateTuple();
    private readonly stateSelector = new TupleSelector(UserServiceStateTuple.tupleName, {});

    private _hasLoaded = false;
    private loadingFinishedSubject = new Subject<void>();

    private _lastUserSubscriptions = [];

    constructor(private router: Router,
                private balloonMsg: Ng2BalloonMsgService,
                private deviceEnrolmentService: DeviceEnrolmentService,
                private tupleService: UserTupleService) {
        super();

        // Continue service initialisation

        // Maintain a list of users, lets hope this doesn't grow too large
        let tupleSelector = new TupleSelector(UserListItemTuple.tupleName, {});
        this.tupleService.observer.subscribeToTupleSelector(tupleSelector)
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: UserListItemTuple[]) => {
                this._users = tuples;
                this._userDisplayNameById = {};
                for (let user of tuples) {
                    this._userDisplayNameById[user.userId] = user.displayName;
                }
            });


        // Setup the onDestroy
        this.onDestroyEvent.subscribe(() => {
                if (this._loggedInStatus['observers'] != null) {
                    for (let observer of this._loggedInStatus['observers']) {
                        observer["unsubscribe"]();
                    }
                }
            }
        );

        this.loadState();
    }

    hasLoaded(): boolean {
        return this._hasLoaded;
    }

    loadingFinishedObservable(): Observable<void> {
        return this.loadingFinishedSubject;
    }

    private loadState(): void {
        this.tupleService.offlineStorage.loadTuples(this.stateSelector)
            .then((tuples: UserServiceStateTuple[]) => {
                let wasLoaded = this._hasLoaded;
                this._hasLoaded = true;

                if (tuples.length != 0) {
                    this.state = tuples[0];
                    // Apply the login
                    if (this.state.userDetails != null)
                        this.setLogin(this.state.userDetails);
                }

                if (!wasLoaded) {
                    this.loadingFinishedSubject.next();
                }

            })
            .catch(e => console.log(`UserService: Error storing state ${e}`));
    }

    private storeState(): void {
        this.tupleService.offlineStorage.saveTuples(this.stateSelector, [this.state])
            .catch(e => console.log(`UserService: Error storing state ${e}`));
    }

    login(userLoginAction: UserLoginAction,
          userDetails: UserListItemTuple): Promise<UserLoginResponseTuple> {

        userLoginAction.deviceToken = this.deviceEnrolmentService.enrolmentToken();


        return this.tupleService.action.pushAction(userLoginAction)
            .then((responses: UserLoginResponseTuple[]) => {
                if (responses == null || responses.length == 0) {
                    throw new Error(
                        "Login process received no tuples from the server"
                    );
                }

                let response = responses[0];

                if (response._tupleType != UserLoginResponseTuple.tupleName) {
                    throw new Error(
                        `Unknown login response tuple ${response.toString()}`
                    );
                }

                if (response.succeeded)
                    this.setLogin(userDetails);

                return response;
            });
    }

    logout(tupleAction: UserLogoutAction): Promise<UserLogoutResponseTuple> {

        if (!this.loggedIn) {
            throw new Error("Can't logout, we're already logged out");
        }

        tupleAction.deviceToken = this.deviceEnrolmentService.enrolmentToken();

        return this.tupleService.action.pushAction(tupleAction)
            .catch(err => {
                if (err.indexOf("not logged in") != -1) {
                    this.setLogout();
                    return;
                }
                throw err;
            })
            .then((responses: UserLogoutResponseTuple[]) => {
                if (responses == null || responses.length == 0) {
                    throw new Error("Logoff process received no tuples from the server");
                }

                let response = responses[0];

                if (response._tupleType != UserLogoutResponseTuple.tupleName) {
                    throw new Error(
                        `Unknown logout response tuple ${response.toString()}`
                    );
                }

                if (response.succeeded)
                    this.setLogout();

                return response;
            });

    }

    private setLogin(userDetails: UserListItemTuple): void {

        // Setup the user logged in subscriptions
        let tupleSelector = new TupleSelector(UserLoggedInTuple.tupleName, {
            userName: userDetails.userId
        });

        this._lastUserSubscriptions.push(
            this.tupleService.observer
                .subscribeToTupleSelector(tupleSelector, true)
                .subscribe((tuples: UserLoggedInTuple[]) => this.userLoggedInReceived(tuples))
        );

        this.state.authToken = "TODO, but not null";
        this.state.userDetails = userDetails;
        this._loggedInStatus.next(true);

        this.storeState();

    }

    private setLogout(): void {
        this.state.userDetails = null;
        this.state.authToken = null;
        this._loggedInStatus.next(false);
        this.storeState();

        // Unsubscribe all the user logged in subscriptions
        while (this._lastUserSubscriptions.length) {
            this._lastUserSubscriptions.pop().unsubscribe();
        }
    }

    private userLoggedInReceived(tuples: UserLoggedInTuple[]): void {
        let data = tuples[0];
        let deviceToken = this.deviceEnrolmentService.enrolmentToken();

        // Do nothing, this is normal
        if (data.deviceToken == deviceToken)
            return;

        this.setLogout();

        // Else, log out
        this.balloonMsg
            .showMessage(
                "This user has been logged out due to a login on another device," +
                " or an administrative logout",
                UsrMsgLevel.Error,
                UsrMsgType.Confirm
            )
            .then(() => this.router.navigate(['peek_core_user', 'login']));

    }

    get loggedInUserDetails(): null | UserListItemTuple {
        if (this.userDetails == null)
            throw new Error("loggedInUserDetails called when it's null");
        return this.userDetails;
    }


    get users() {
        return this._users;
    }

    userDisplayName(userName: string) {
        if (this._userDisplayNameById.hasOwnProperty(userName))
            return this._userDisplayNameById[userName];
        return null;
    }

    get userDetails(): null | UserListItemTuple {
        return this.state.userDetails;
    }

    isLoggedIn() {
        return this.loggedIn;
    }

    get loggedIn(): boolean {
        return this.state.authToken != null;
    }

    get loggedInStatus(): Subject<boolean> {
        return this._loggedInStatus;
    }


}