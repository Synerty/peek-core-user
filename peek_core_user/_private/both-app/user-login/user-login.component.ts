import {Router} from "@angular/router";
import {
    UserListItemTuple,
    UserLoginAction,
    UserLoginResponseTuple,
    UserService
} from "@peek/peek_core_user";
import {UserTupleService} from "@peek/peek_core_user/_private/user-tuple.service";
import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter, TupleSelector} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js"
import { TitleService } from "@synerty/peek-plugin-base-js"
import {UserLoginUiSettingTuple} from "../tuples/UserLoginUiSettingTuple";
import {DeviceEnrolmentService} from "@peek/peek_core_device";

@Component({
    selector: './peek-core-user-login',
    templateUrl: './user-login.component.dweb.html',
    styleUrls: ['../scss/plugin-user.dweb.scss'],
    moduleId: module.id
})
export class UserLoginComponent extends ComponentLifecycleEventEmitter {

    users: Array<UserListItemTuple> = [];
    selectedUser: UserLoginAction = new UserLoginAction();
    isAuthenticating: boolean = false;
    test: any = "";

    errors: string[] = [];

    warnings: string[] = [];
    warningKeys: string[] = [];

    setting: UserLoginUiSettingTuple = new UserLoginUiSettingTuple();

    constructor(private balloonMsg: BalloonMsgService,
                private deviceEnrolmentService: DeviceEnrolmentService,
                private tupleService: UserTupleService,
                private userService: UserService,
                private router: Router,
                titleService: TitleService) {
        super();
        titleService.setTitle("User Login");

        let selectAUser = new UserListItemTuple();
        selectAUser.displayName = "Select a User";


        let ts = new TupleSelector(UserLoginUiSettingTuple.tupleName, {});
        this.tupleService.observer.subscribeToTupleSelector(ts)
            .takeUntil(this.onDestroyEvent)
            .filter(items => items.length != 0)
            .subscribe((tuples: UserLoginUiSettingTuple[]) => {
                this.setting = tuples[0];
                if (this.setting.showUsersAsList)
                    this.loadUsersList();
            });
    }

    private loadUsersList(): void {


        let tupleSelector = new TupleSelector(UserListItemTuple.tupleName, {});
        this.tupleService.observer.subscribeToTupleSelector(tupleSelector)
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: UserListItemTuple[]) => {
                let blank = new UserListItemTuple();
                blank.displayName = '--- select ---';
                this.users = [blank];
                this.users.add(tuples);
                console.log("UserListItemTuple Tuples len = " + tuples.length.toString());
            });
    }

    isSelectedUserNull(): boolean {
        return this.selectedUser.userName == null || this.selectedUser.userName === '';
    }

    isUserSelected(item: UserListItemTuple): boolean {
        if (this.isSelectedUserNull())
            return false;
        return this.selectedUser.userName == item.userId
    }

    webDisplayText(item: UserListItemTuple): string {
        if (item.userId == null || item.userId === '')
            return item.displayName; // For the --select-- case

        return `${item.displayName} (${item.userId})`;

    }

    loginText() {
        return "Login";
    }

    isLoginEnabled(): boolean {
        const isPassSet = this.selectedUser.password
            && this.selectedUser.password.length != 0;

        const isVehicleSet = !this.setting.showVehicleInput
            || this.selectedUser.vehicleId && this.selectedUser.vehicleId.length != 0
            || !this.deviceEnrolmentService.isFieldService();

        return !this.isSelectedUserNull()
            && !this.isAuthenticating
            && isPassSet
            && isVehicleSet;
    }

    doLogin() {
        if (!this.isLoginEnabled())
            return;

        let tupleAction = this.selectedUser;

        // Add any warnings
        tupleAction.acceptedWarningKeys = this.warningKeys;

        this.isAuthenticating = true;
        this.userService.login(tupleAction)
            .then((response: UserLoginResponseTuple) => {

                if (response.succeeded) {
                    this.balloonMsg.showSuccess("Login Successful");
                    this.router.navigate(['']);
                    return;
                }

                this.balloonMsg.showWarning("Login Failed, check the warnings and try again");

                this.errors = response.errors;
                this.warnings = [];
                for (let key in response.warnings) {
                    if (!response.warnings.hasOwnProperty(key))
                        continue;
                    for (let item of response.warnings[key].split('\n')) {
                        this.warnings.push(item);
                    }
                    this.warningKeys.push(key);
                }
                this.isAuthenticating = false;

            })
            .catch((err) => {
                if (err.toString().startsWith("Timed out")) {
                    alert("Login Failed. The server didn't respond.");
                    this.isAuthenticating = false;
                    return;
                } else if (err.toString().length == 0) {
                    alert("An error occurred when logging in.");
                }
                alert(err);
                this.isAuthenticating = false;
            });

    }


}
