import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { MatSelectModule } from '@angular/material/select';
import { AppComponent } from './app.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
//import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatNativeDateModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { DetailsComponent } from './details/details.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterModule, Routes } from '@angular/router';
import { SearchComponent } from './search/search.component';
import { MatSliderModule } from '@angular/material/slider';
import { GenreListResolver } from './search/resolvers/genre-list.resolver';
import { HttpClientModule } from '@angular/common/http';
import { ListComponent } from './list/list.component';
import { PlatformListResolver } from './search/resolvers/platforms.resolver';
import { VjsComponent } from './details/vjs/vjs.component';
import { IpDataResolver } from './search/resolvers/ip-data.resolver';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MomentDateAdapter } from '@angular/material-moment-adapter';

const routes: Routes = [
    {
        path: "search",
        component: SearchComponent,
        resolve: {
            genres: GenreListResolver,
            platforms: PlatformListResolver,
            ipData: IpDataResolver
        },
        data: { title: "Search" }
    },
    {
        path: '',
        redirectTo: 'search',
        pathMatch: 'full',
    }
];

export const MY_DATE_FORMAT = {
    parse: {
      dateInput: 'YYYY-MM-DD',
    },
    display: {
      dateInput: 'DD/MM/YYYY',
      monthYearLabel: 'MMM YYYY',
      dateA11yLabel: 'LL',
      monthYearA11yLabel: 'MMMM YYYY',
    },
};

@NgModule({
    declarations: [
        AppComponent,
        SearchComponent,
        DetailsComponent,
        ListComponent,
        VjsComponent
    ],
    imports: [
        RouterModule.forRoot(routes),
        BrowserModule,
        BrowserAnimationsModule,
        MatSelectModule,
        FormsModule,
        ReactiveFormsModule,
        MatDatepickerModule,
        MatFormFieldModule,
        MatNativeDateModule,
        MatButtonModule,
        MatIconModule,
        MatInputModule,
        MatSidenavModule,
        MatListModule,
        MatToolbarModule,
        MatSliderModule,
        HttpClientModule
    ],
    exports: [
        DetailsComponent,
        ListComponent
    ],
    providers: [
        { provide: DateAdapter, useClass: MomentDateAdapter, deps: [MAT_DATE_LOCALE] },
        { provide: MAT_DATE_FORMATS, useValue: MY_DATE_FORMAT }
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
