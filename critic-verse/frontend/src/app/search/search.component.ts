import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDrawer } from '@angular/material/sidenav';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html'
})
export class SearchComponent implements OnInit, OnDestroy  {
  form: FormGroup;
  maxUserVotes: number = 0;
  maxCriticVotes: number = 0;
  genres: string[] = [];
  items: any;

  private _unsubscribeAll: Subject<any> = new Subject<any>();

  @ViewChild('drawer') drawer!: MatDrawer;

  constructor(
    private _fb: FormBuilder,
    private _route: ActivatedRoute
  ) {
    this.form = this._fb.group({
      searchQuery: [''],
      selectedOption: [''],
      selectedGenres: new FormControl([]),
      selectedDate: ['']
    });
  }

  ngOnInit(): void {
    this._route.data.pipe(takeUntil(this._unsubscribeAll)).subscribe((resolve: any) => {
      this.maxUserVotes = resolve.maxUserVotes;
      this.maxCriticVotes = resolve.maxCriticVotes;
      this.genres = resolve.genres;
      this.items = resolve.items;
    })
  }

  ngOnDestroy(): void {
      this._unsubscribeAll.next(undefined);
      this._unsubscribeAll.complete();
  }


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
