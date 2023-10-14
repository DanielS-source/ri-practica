import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {MatSelectModule} from '@angular/material/select';
import { AppComponent } from './app.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatNativeDateModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { DetailsComponent } from './details/details.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import {MatListModule} from '@angular/material/list';
import {MatToolbarModule} from '@angular/material/toolbar';
import { RouterModule, Routes } from '@angular/router';
import { SearchComponent } from './search/search.component';
import {MatSliderModule} from '@angular/material/slider';

const routes: Routes = [
  {
    path: "search",
    component: SearchComponent,
    data: { title: "Search" }
  },
  { path: "", redirectTo: "/search", pathMatch: "full" }
];

@NgModule({
  declarations: [
    AppComponent,
    SearchComponent,
    DetailsComponent
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
    MatSliderModule
  ],
  exports: [DetailsComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
