import {Router} from "@angular/router";
import {
    UserService,
    UserLogoutAction,
    UserLogoutResponseTuple
} from "@peek/peek_core_user";
import {
    UserTupleService
} from "@peek/peek_core_user/_private/user-tuple.service";
import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter, TupleActionPushService} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js"
import { TitleService } from "@synerty/peek-plugin-base-js"


@Component({
    selector: './peek-core-user-logout',
    templateUrl: './user-logout.component.dweb.html',
    styleUrls: ['../scss/plugin-user.dweb.scss'],
    moduleId: module.id
})
export class UserLogoutComponent extends ComponentLifecycleEventEmitter {

    isAuthenticating: boolean = false;

    errors: string[] = [];

    warnings: string[] = [];
    warningKeys: string[] = [];

    constructor(private balloonMsg: BalloonMsgService,
                private tupleService: UserTupleService,
                private userService: UserService,
                private router: Router,
                titleService: TitleService) {
        super();
        titleService.setTitle("User Logout");


    }

    doLogout() {
        let tupleAction = new UserLogoutAction();
        tupleAction.userName = this.userService.userDetails.userId;

        // Add any warnings
        tupleAction.acceptedWarningKeys = this.warningKeys;

        this.isAuthenticating = true;
        this.userService.logout(tupleAction)
            .then((response: UserLogoutResponseTuple) => {

                if (response.succeeded) {
                    this.balloonMsg.showSuccess("Logout Successful");
                    this.router.navigate(['']);
                    return;
                }

                this.balloonMsg.showWarning("Logout Failed, check the warnings and try again");

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
                if (err.startsWith("Timed out")) {
                    alert("Logout Failed. The server didn't respond.");
                    this.isAuthenticating = false;
                    return;
                }
                alert(err);
                this.isAuthenticating = false;
            });

    }

    // ------------------------------
    // Display methods

    loggedInUserText() {
        return this.userService.userDetails.displayName
            + ` (${this.userService.userDetails.userId})`;
    }


}
