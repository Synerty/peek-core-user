import { UserLoginComponent } from "./user-login/user-login.component";
import { LoggedInGuard, LoggedOutGuard } from "@peek/peek_core_user";
import { UserLogoutComponent } from "./user-logout/user-logout.component";
import { Route } from "@angular/router";

export const pluginRoutes: Route[] = [
    {
        path: "",
        pathMatch: "full",
        component: UserLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "login",
        component: UserLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "logout",
        component: UserLogoutComponent,
        canActivate: [LoggedInGuard],
    },
    // Fall through to peel-client-fe UnknownRoute
];
