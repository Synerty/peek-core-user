import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {UserLogoutComponent} from "./user-logout.component";
import {PeekModuleFactory} from "@synerty/peek-util-web";


@NgModule({
    imports: [
        CommonModule,
        ...PeekModuleFactory.FormsModules
    ],
    exports: [UserLogoutComponent],
    declarations: [UserLogoutComponent]
})
export class UserLogoutModule {
}
