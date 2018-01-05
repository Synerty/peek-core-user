import {Injectable} from "@angular/core";
import {CanActivate, Router} from "@angular/router";
import {UserService} from "./user.service";

@Injectable()
export class LoggedOutGuard implements CanActivate {
    constructor(private user: UserService, private router:Router) {
    }

    canActivate() {
        if (!this.user.isLoggedIn())
            return true;

        this.router.navigate(['peek_plugin_user', 'logout']);
        return false;
    }
}