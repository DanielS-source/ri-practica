import { Component, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatDrawer } from '@angular/material/sidenav';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html'
})
export class SearchComponent {
  form: FormGroup;
  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      searchQuery: [''],
      selectedOption: [''],
      selectedDate: ['']
    });
  }

  @ViewChild('drawer') drawer!: MatDrawer;

  submitForm() {
    const formData = this.form.value;
    console.log('Form Data:', formData);
    this.openDrawer();
  }

  openDrawer() {
    this.drawer.open();
  }

  closeDrawer() {
    this.drawer.close();
  }
}
