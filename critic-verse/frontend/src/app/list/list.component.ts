import { Component, Input, ViewChild } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';

@Component({
    selector: 'app-list',
    templateUrl: './list.component.html'
})
export class ListComponent {

    @Input() items: any[] = [];

    @ViewChild('drawer') sidenav!: MatSidenav;

    selectedItem: any;

    setItem(item: any): void {
        this.selectedItem = item;
        this.sidenav.open();
    }

    closeDrawer(): void {
        console.log('hi')
        this.sidenav.close();
    }

}
