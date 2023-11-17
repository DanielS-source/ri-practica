import { Component, ElementRef, OnDestroy, OnInit, Renderer2, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { SearchService } from './search.service';
import { GameItem, GameQuery, IPData, SuggestionQuery } from './search.model';
import * as moment from 'moment';
import { animate, style, transition, trigger } from '@angular/animations';

@Component({
    selector: 'app-search',
    templateUrl: './search.component.html',
    animations: [
        trigger(
          'showAnimation', [
            transition(':enter', [
              style({opacity: 0}),
              animate('1000ms ease', style({opacity: 1}))
            ]),
            transition(':leave', [
              style({opacity: 1}),
              animate('500ms ease-out', style({opacity: 0}))
            ])
          ]
        )
    ]
})
export class SearchComponent implements OnInit, OnDestroy {
    form: FormGroup;
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
    ipData!: IPData;
    suggestions: string[] = [];
    alternatives: string[] = [];
    suggestionContainer: boolean = false;
    suggestion: any;
    separator: any;
    showAlternatives: boolean = true;
    sortTypes: {
        label: string,
        value: string,
    }[] = [
        {
            label:"Critic Score",
            value: "metascore"
        },
        {
            label:"User Score",
            value: "user_score"
        },
        {
            label:"Release Date",
            value: "release_date"
        },
        {
            label:"Title",
            value: "title"
        }
    ];
    sortDirections: string[] = [
        "Ascending",
        "Descending"
    ];
    sortDir: string = "Descending";

    dateFormat: string = "YYYY-MM-DD";

    private _unsubscribeAll: Subject<any> = new Subject<any>();

    //@ViewChild('drawer') drawer!: MatDrawer;
    @ViewChild('suggestions') suggestionsResults!: ElementRef;

    constructor(
        private _fb: FormBuilder,
        private _route: ActivatedRoute,
        private _searchService: SearchService,
        private renderer: Renderer2
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
            sort_by: null,
            sort_direction: null,
        });
    }

    ngOnInit(): void {
        this._route.data.pipe(takeUntil(this._unsubscribeAll)).subscribe((resolve: any) => {
            this.genres = resolve.genres;
            this.platforms = resolve.platforms;
            this.ipData = resolve.ipData;
            this.card_image = resolve.card_image;
            this.updatePageControls();
            this.updateForm()
            this.initializeItems();
        });
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
            sort_by: "metascore",
            sort_direction: this.sortDirections[this.sortDirections.length - 1],
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

        if (query.start_date instanceof Date) {
            query.start_date = moment(query.start_date).format(this.dateFormat);
        }

        if (query.end_date instanceof Date) {
            query.end_date = moment(query.end_date).format(this.dateFormat);
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

    personalization(query: GameQuery) {
        // Customize the results based on the country or the continent of the user.
        if(this.ipData.country !== null || this.ipData.continentName !== null) {
            // Metacritic specific query
            if(this.ipData.country === 'Japan' || this.ipData.country === 'Korea' || this.ipData.country === 'Australia')
                query.country = this.ipData.country;
            else if(this.ipData.continentName !== null)
                query.country = this.ipData.continentName;
        }
    }

    initializeItems() {
        const query: GameQuery = { ...this.form.value };

        this.personalization(query);

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
        query.title = this.form.controls["title"].value;
        
        if(page > 0) query.page = this.page;

        this.personalization(query);

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

        if (query.start_date instanceof moment) {
            query.start_date = moment(query.start_date).format(this.dateFormat);
        }

        if (query.end_date instanceof moment) {
            query.end_date = moment(query.end_date).format(this.dateFormat);
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

    /* Suggestion logic */

    showSuggestionContainer() {
        if(this.form.controls["title"].value != null) {
            if(this.suggestionContainer == false && this.form.controls["title"].value.length > 0) {
                this.suggestionContainer = true;
                this.loadSuggestions();
            }
        }
    }

    normalizeContent(data: string) {
        if(data != null && data.length > 0) {
            data = String(data).replaceAll("<b>", "").replaceAll("</b>", "");
        }
        return data;
    }

    createSuggestion(title: string) {
        const formattedTitle = this.normalizeContent(title);
        this.suggestion = this.renderer.createElement('div');
        this.renderer.setAttribute(this.suggestion, 'class', 'suggestion p-1 cursor-pointer');
        this.renderer.setAttribute(this.suggestion, 'title', formattedTitle);
        this.renderer.listen(this.suggestion, 'click', ()=>{ this.onSuggestionClick(formattedTitle); });
        this.suggestion.innerHTML = title;
        this.renderer.appendChild(this.suggestionsResults.nativeElement, this.suggestion);
    }

    onSuggestionClick(element: string) {
        this.form.controls["title"].setValue(element);
        this.hideSuggestionContainer();
    }

    createSeparator() {
        this.separator = this.renderer.createElement('hr');
        this.renderer.setAttribute(this.separator, 'class', 'border-[#424242]/50 w-[10vw] m-auto');
        this.renderer.appendChild(this.suggestionsResults.nativeElement, this.separator);
    }

    loadSuggestions() {
        const sQuery: SuggestionQuery = { "title": this.form.controls["title"].value };
        this.suggestions = [];
        this.alternatives = [];
        this._searchService.getSuggestions(sQuery)
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((response: any) => {
                this.suggestions = response.suggestions.map((hit: { _source: any }) => hit._source.title_search);
                this.alternatives = [];
                if(response.hits.length > 0)
                    this.alternatives = response.hits.map((hit: { highlight: any }) =>  hit.highlight.title_search);
                if(this.suggestions.length > 0) {
                    this.showAlternatives = false;
                    this.suggestionsResults.nativeElement.innerHTML = "";
                    this.suggestions.forEach(suggestion => {
                        if(this.suggestionsResults.nativeElement.innerHTML.length > 0)
                            this.createSeparator();
                        this.createSuggestion(suggestion);
                    });
                }else if(this.alternatives.length > 0) {
                    this.showAlternatives = true;
                    this.suggestionsResults.nativeElement.innerHTML = "";
                    this.alternatives.forEach(alternative => {
                        if(this.suggestionsResults.nativeElement.innerHTML.length > 0)
                            this.createSeparator();
                        this.createSuggestion(alternative);
                    });
                }else{
                    if(this.suggestionContainer) {
                        this.suggestionsResults.nativeElement.innerHTML = "No suggestions";
                        this.hideSuggestionContainer();
                    }
                }
            });
    }

    hideSuggestionContainer() {
        this.suggestionContainer = false;
    }

    /* End suggestion logic */

}
