import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDrawer } from '@angular/material/sidenav';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { SearchService } from './search.service';
import { GameItem, GameQuery } from './search.model';

@Component({
    selector: 'app-search',
    templateUrl: './search.component.html'
})
export class SearchComponent implements OnInit, OnDestroy {
    form: FormGroup;
    maxUserVotes: number = 0;
    maxCriticVotes: number = 0;
    genres: string[] = [];
    platforms: string[] = [];
    items: GameItem[] = [];
    time: number = 0;
    count: number = 0;
    page: number = 0;
    nPages: number = 0;
    size: number = 0;
    card_image: string[] = [];
    previousBtn: boolean = true;
    nextBtn: boolean = false;

    private _unsubscribeAll: Subject<any> = new Subject<any>();

    @ViewChild('drawer') drawer!: MatDrawer;

    constructor(
        private _fb: FormBuilder,
        private _route: ActivatedRoute,
        private _searchService: SearchService
    ) {
        this.form = this._fb.group({
            title: null,
            genres: new FormControl([]),
            platforms: new FormControl([]),
            start_date: null,
            end_date: null,
            user_score_min: 0,
            user_score_max: 10,
            critic_score_min: 0,
            critic_score_max: 100,
            user_reviews_min: 0,
            user_reviews_max: 0,
            critic_reviews_min: 0,
            critic_reviews_max: 0,
        });
    }

    ngOnInit(): void {
        this._route.data.pipe(takeUntil(this._unsubscribeAll)).subscribe((resolve: any) => {
            this.maxUserVotes = resolve.maxUserVotes;
            this.maxCriticVotes = resolve.maxCriticVotes;
            this.genres = resolve.genres;
            this.platforms = resolve.platforms;
            this.items = resolve.items["items"];
            this.card_image = resolve.card_image;
            this.time = resolve.items["time"];
            this.count = resolve.items["n_hits"];
            this.page = resolve.items["page"];
            this.nPages = resolve.items["n_pages"];
            this.size = resolve.items["size"];
            this.updatePageControls();
            this.updateForm()
        })
    }

    previousPage() {
        this.page -= 1;
        this.submitForm(this.page);
    }

    nextPage() {
        this.page += 1;
        this.submitForm(this.page);
    }

    updateForm() {
        this.form.patchValue({
            user_reviews_min: 0,
            user_reviews_max: this.maxUserVotes,
            critic_reviews_min: 0,
            critic_reviews_max: this.maxCriticVotes
        })
    }

    ngOnDestroy(): void {
        this._unsubscribeAll.next(undefined);
        this._unsubscribeAll.complete();
    }

    updatePageControls() {
        this.previousBtn = (this.page == 0);
        this.nextBtn = !(this.page < this.nPages);
    }

    submitFormKeepPage() {
        const query: GameQuery = { ...this.form.value };
        query.page = this.page;

        if (Array.isArray(query.genres) && query.genres.length > 0) {
            query.genre = query.genres.join(', ');
        } else {
            query.genre = null;
        }
        delete query.genres;

        if (Array.isArray(query.platforms) && query.platforms.length > 0) {
            query.platform = query.platforms.join(', ');
        } else {
            query.platform = null;
        }
        delete query.platforms;

        const dateOptions: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };

        if (query.start_date instanceof Date) {
            query.start_date = query.start_date.toLocaleDateString('es-ES', dateOptions).split('/').reverse().join('-');
        }

        if (query.end_date instanceof Date) {
            query.end_date = query.end_date.toLocaleDateString('es-ES', dateOptions).split('/').reverse().join('-');
        }

        this._searchService.searchItems(query)
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((response: any) => {
                this.items = response.hits.map((hit: { _source: any }) => hit._source);
                this.time = response.time;
                this.count = response.n_hits;
                this.page = response.page;
                this.nPages = response.n_pages;
                this.size = response.size;
                
                this.updatePageControls();
            });
    }

    submitForm(page: number) {
        const query: GameQuery = { ...this.form.value };
        if(page > 0) query.page = this.page;

        if (Array.isArray(query.genres) && query.genres.length > 0) {
            query.genre = query.genres.join(', ');
        } else {
            query.genre = null;
        }
        delete query.genres;

        if (Array.isArray(query.platforms) && query.platforms.length > 0) {
            query.platform = query.platforms.join(', ');
        } else {
            query.platform = null;
        }
        delete query.platforms;

        const dateOptions: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };

        if (query.start_date instanceof Date) {
            query.start_date = query.start_date.toLocaleDateString('es-ES', dateOptions).split('/').reverse().join('-');
        }

        if (query.end_date instanceof Date) {
            query.end_date = query.end_date.toLocaleDateString('es-ES', dateOptions).split('/').reverse().join('-');
        }

        this._searchService.searchItems(query)
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((response: any) => {
                this.items = response.hits.map((hit: { _source: any }) => hit._source);
                this.time = response.time;
                this.count = response.n_hits;
                this.page = response.page;
                this.nPages = response.n_pages;
                this.size = response.size;
                
                this.updatePageControls();
            });
    }

}
