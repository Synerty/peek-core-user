import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {Routes, RouterModule} from "@angular/router";
import {EditInternalUserComponent} from "./edit-internal-user-table/edit.component";
import {EditInternalGroupComponent} from "./edit-internal-group-table/edit.component";
import {EditSettingComponent} from "./edit-setting-table/edit.component";



import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService
} from "@synerty/vortexjs";
// Import our components
import {UserComponent} from "./user.component";
import {
    userObservableName, userFilt, userActionProcessorName
} from "@peek/peek_plugin_user/_private";


export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(userObservableName, userFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(userActionProcessorName, userFilt);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: '',
        component: UserComponent
    }

];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule
    ],
    exports: [],
    providers: [
        TupleDataObserverService, {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory
        },
        TupleActionPushService, {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory
        }
    ],
    declarations: [UserComponent,
        EditInternalUserComponent,
        EditInternalGroupComponent,
        EditSettingComponent]
})
export class UserModule {

}
