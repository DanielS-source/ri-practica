import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
    selector: 'app-details',
    templateUrl: './details.component.html'
})
export class DetailsComponent {

    @Input() item: any;

    @Output() closeDrawerEvent = new EventEmitter<void>();

    closeDrawer() {
        this.closeDrawerEvent.emit();
    }
}
