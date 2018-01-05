import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {UserLoginComponent} from "./user-login.component";
import {PeekModuleFactory} from "@synerty/peek-util/index.web";


@NgModule({
    imports: [
        CommonModule,
        ...PeekModuleFactory.FormsModules
    ],
    exports: [UserLoginComponent],
    declarations: [UserLoginComponent]
})
export class UserLoginModule {
}
