import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private _httpClient: HttpClient) { }

  getAllItems(): Observable<any[]> {
    return this._httpClient.get<any[]>(`${environment.api}/search?size=${environment.pageSize}`, this.httpOptions)
      .pipe(
        map((response: any) => response)
      );
  }

  getMaxUserVotes(): Observable<number> {
    // user_reviews
    return this._httpClient.get<any>(
      `${environment.api}/user_score?max=true`,
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.max_user_reviews.value)
    );
  }

  getMaxCriticVotes(): Observable<number> {
    // critic-reviews
    return this._httpClient.get<any>(
      `${environment.api}/metascore?max=true`,
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.max_user_reviews.value)
    );
  }

  getGenreList(): Observable<string[]> {
    // genre list
    return this._httpClient.get<any>(
      `${environment.api}/genres`,
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.unique_genres.buckets.map((bucket: { key: string; }) => bucket.key))
    );
  }
}
