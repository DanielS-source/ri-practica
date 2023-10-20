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
        map((response: any) => response.hits.map((hit: { _source: any; }) => hit._source))
        // map((response: any) => response.hits.hits.map((hit: { _source: any; }) => hit._source))
      );
  }

  getMaxUserVotes(): Observable<number> {
    return this._httpClient.get<any>(
      `${environment.api}/user_score?max=true`,
      this.httpOptions
    ).pipe(
      map((response: any) => response)
    );
  }

  getMaxCriticVotes(): Observable<number> {
    return this._httpClient.get<any>(
      `${environment.api}/metascore?max=true`,
      this.httpOptions
    ).pipe(
      map((response: any) => response)
    );
  }

  getGenreList(): Observable<string[]> {
    return this._httpClient.get<any>(
      `${environment.api}/genres`,
      this.httpOptions
    ).pipe(
      map((response: any) => response)
    );
  }
}
