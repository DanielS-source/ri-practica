import { Component, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDrawer } from '@angular/material/sidenav';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  form: FormGroup;
  options: { value: string; label: string }[] = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ];

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      searchQuery: [''],
      selectedOption: [''],
      selectedDate: ['']
    });
  }

  @ViewChild('drawer') drawer!: MatDrawer;

  submitForm() {
    // Handle form submission here
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
