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
    return this._httpClient.get<any[]>(`${environment.api}/${environment.index}/_search?size=${environment.pageSize}`, this.httpOptions)
      .pipe(
        map((response: any) => response.hits.hits.map((hit: { _source: any; }) => hit._source))
      );
  }

  getMaxUserVotes(): Observable<number> {
    const query = {
      size: 0,
      aggs: {
        max_user_reviews: {
          max: {
            field: 'user_reviews'
          }
        }
      }
    };
    return this._httpClient.post<any>(
      `${environment.api}/${environment.index}/_search?size=${environment.pageSize}`,
      JSON.stringify(query),
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.max_user_reviews.value)
    );
  }

  getMaxCriticVotes(): Observable<number> {
    const query = {
      size: 0,
      aggs: {
        max_user_reviews: {
          max: {
            field: 'critic_reviews'
          }
        }
      }
    };
    return this._httpClient.post<any>(
      `${environment.api}/${environment.index}/_search?size=${environment.pageSize}`,
      JSON.stringify(query),
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.max_user_reviews.value)
    );
  }

  getGenreList(): Observable<string[]> {
    const query = {
      size: 0,
      aggs: {
        unique_genres: {
          terms: {
            field: 'genre'
          }
        }
      }
    };
    return this._httpClient.post<any>(
      `${environment.api}/${environment.index}/_search?size=${environment.pageSize}`,
      JSON.stringify(query),
      this.httpOptions
    ).pipe(
      map((response: any) => response.aggregations.unique_genres.buckets.map((bucket: { key: string; }) => bucket.key))
    );
  }
}
