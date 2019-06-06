import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {PeekModuleFactory} from "@synerty/peek-util-web";
import {UserLoginModule} from "./user-login/user-login.module";
import {UserLogoutModule} from "./user-logout/user-logout.module";
import {pluginRoutes} from "./plugin-user.routes";
import {
    LoggedInGuard,
    LoggedOutGuard,
    ProfileService,
    userActionProcessorName,
    userObservableName,
    userFilt,
    UserService
} from "@peek/peek_core_user";

import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";


@NgModule({
    imports: [
        // Angular
        CommonModule,
        // Web and NativeScript
        PeekModuleFactory.RouterModule,
        PeekModuleFactory.RouterModule.forChild(pluginRoutes),
        ...PeekModuleFactory.FormsModules,
        // This plugin
        UserLoginModule,
        UserLogoutModule
    ],
    declarations: [],
    providers: [
    ]
})
export class PluginUserModule {
}