import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';
import { GameItem, GameQuery, SearchItem } from './search.model';

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

    getAllItems(): Observable<SearchItem> {
        return this._httpClient.get<SearchItem[]>(`${environment.api}/?size=${environment.pageSize}`, this.httpOptions)
            .pipe(
                map((response: any) => {
                    return {
                      time: response.time,
                      size: response.size,
                      n_pages: response.n_pages,
                      page: response.page,
                      n_hits: response.n_hits,
                      items: response.hits.map((hit: { _source: any; }) => hit._source)
                    };
                })
            );
    }

    getMaxUserVotes(): Observable<number> {
        return this._httpClient.get<any>(
            `${environment.api}/user-reviews?max=true`,
            this.httpOptions
        ).pipe(
            map((response: any) => response)
        );
    }

    getMaxCriticVotes(): Observable<number> {
        return this._httpClient.get<any>(
            `${environment.api}/critic-reviews?max=true`,
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

    getPlatformList(): Observable<string[]> {
        return this._httpClient.get<any>(
            `${environment.api}/platforms`,
            this.httpOptions
        ).pipe(
            map((response: any) => response)
        );
    }

    searchItems(query: GameQuery): Observable<any> {
        return this._httpClient.post<any>(`${environment.api}/search`, query, this.httpOptions);
    }
}
