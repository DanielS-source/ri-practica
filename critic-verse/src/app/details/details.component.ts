import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html'
})
export class DetailsComponent {
  @Output() closeDrawerEvent = new EventEmitter<void>();

  closeDrawer() {
    this.closeDrawerEvent.emit();
  }
}
