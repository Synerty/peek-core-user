import {Injectable} from "@angular/core";
import {CanActivate, Router} from "@angular/router";
import {UserService} from "./user.service";
import {DeviceEnrolmentService, DeviceInfoTuple} from "@peek/peek_core_device";

@Injectable()
export class LoggedInGuard implements CanActivate {
    constructor(private user: UserService,
                private router:Router,
                private deviceEnrolmentService: DeviceEnrolmentService) {
    }

    canActivate() {
        if (!this.user.hasLoaded()) {
            return new Promise<boolean>((resolve, reject) => {
                this.user.loadingFinishedObservable()
                    .first()
                    .subscribe(() => {
                        resolve(this.canActivate());
                    });
            });
        }

        if (this.user.isLoggedIn())
            return true;

        if (this.deviceEnrolmentService.isSetup()) {
            console.log("logged-in.guard");
            this.router.navigate(['peek_core_user', 'login']);
        }
        return false;
    }
}


