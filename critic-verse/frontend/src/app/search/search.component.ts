import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDrawer } from '@angular/material/sidenav';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { SearchService } from './search.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html'
})
export class SearchComponent implements OnInit, OnDestroy  {
  form: FormGroup;
  maxUserVotes: number = 0;
  maxCriticVotes: number = 0;
  genres: string[] = [];
  items: any[] = [];
  card_image: string[] = [];

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
      this.items = resolve.items;
      this.card_image = resolve.card_image;
      this.updateForm()
      console.log(resolve)
    })
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

  submitForm() {
    let genres, s_date, e_date;
    const formData = this.form.value;
    if(Array.isArray(formData.genres) && formData.genres.length > 0) {
      let genres = formData.genres.join(", ");
      formData.genre = genres;
    }else formData.genre = null;
    if(formData.start_date instanceof Date) {
      let s_date = formData.start_date.toLocaleDateString('es-ES', {year: 'numeric', month: '2-digit', day: '2-digit'}).replaceAll("\/", "-");
      formData.start_date = s_date;
    }
    if(formData.end_date instanceof Date) {
      let e_date = formData.end_date.toLocaleDateString('es-ES', {year: 'numeric', month: '2-digit', day: '2-digit'}).replaceAll("\/", "-");
      formData.end_date = e_date;
    }
    console.log('Form Data:', formData);
    this._searchService.searchItems(formData).pipe(takeUntil(this._unsubscribeAll)).subscribe((response: any) => {
      console.log(response);
      this.items = response.hits.map((hit: { _source: any; }) => hit._source);
    });
  }
}
