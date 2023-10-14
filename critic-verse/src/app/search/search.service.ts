import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  constructor(private _httpClient: HttpClient) { }

  getAllItems(): Observable<any[]> {
    return this._httpClient.get(`${environment.api}/${environment.index}/_search?size=${environment.pageSize}`).pipe(
      map((response: any) => response)
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
    return this._httpClient.post(`${environment.api}/${environment.index}/_search?size=${environment.pageSize}`, JSON.stringify(query)).pipe(
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
    return this._httpClient.post(`${environment.api}/${environment.index}/_search?size=${environment.pageSize}`, JSON.stringify(query)).pipe(
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
    return this._httpClient.post(`${environment.api}/${environment.index}/_search?size=${environment.pageSize}`, JSON.stringify(query))
    .pipe(
      map((response: any) => response.aggregations.unique_genres.buckets.map((bucket: { key: string; }) => bucket.key))
    );
  }


}
