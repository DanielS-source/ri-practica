import { Component, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { SearchService } from '../search/search.service';

@Component({
    selector: 'app-list',
    templateUrl: './list.component.html'
})
export class ListComponent {

    @Input() items: any[] = [];
    @Input() time: number = 0;
    @Input() count: number = 0;
    @Input() page: number = 0;
    @Input() previousBtn: boolean = false;
    @Input() nextBtn: boolean = false;

    @ViewChild('drawer') sidenav!: MatSidenav;

    selectedItem: any;

    constructor(private _searchService: SearchService) {

    }

    @Output() callPreviousPage: EventEmitter<void> = new EventEmitter<void>();
    @Output() callNextPage: EventEmitter<void> = new EventEmitter<void>();

    previousPage() {
      this.callPreviousPage.emit();
    }

    nextPage() {
        this.callNextPage.emit();
    }

    setItem(item: any) {
        // Set document as relevant
        this._searchService.addRelevance(item.title_search).subscribe((resolve: any) => {});

        this.selectedItem = item;
        this.sidenav.open();
    }

    closeDrawer(): void {
        this.sidenav.close();
    }

}
