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
    return this._httpClient.get<any[]>(`${environment.api}/?size=${environment.pageSize}`, this.httpOptions)
      .pipe(
        map((response: any) => response.hits.map((hit: { _source: any; }) => hit._source))
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

  searchItems(formData: any): Observable<any> {
    /**
     * title: str = Query(None, description="Title", ),
    title_asc: bool = Query(None, description="Title asc (True) / desc (False)", ),
    genre: str = Query(None, description="Genre (Use commas for multiples genres)", ),
    platform: str = Query(None, description="Platforms (Use commas for multiples platforms)", ),
    country: str = Query(None, description="Countries (Use commas for multiples countries)", ),
    metascore_min: int = Query(None, description="Metascore min", ),
    metascore_max: int = Query(None, description="Metascore max", ),
    critic_reviews_min: int = Query(None, description="Metascore reviews min", ),
    critic_reviews_max: int = Query(None, description="Metascore reviews max", ),
    metascore_asc: bool = Query(None, description="Metascore asc (True) / desc (False)", ),
    user_score_min: int = Query(None, description="User score min", ),
    user_score_max: int = Query(None, description="User score max", ),
    user_reviews_min: int = Query(None, description="User reviews min", ),
    user_reviews_max: int = Query(None, description="User reviews max", ),
    user_score_asc: bool = Query(None, description="User score asc (True) / desc (False)", ),
    start_date: datetime.date = Query(None, description="Start date", ),
    end_date: datetime.date = Query(None, description="End date", ),
    date_asc: bool = Query(None, description="Date asc (True) / desc (False)", ),
    page: int = Query(0, description="Page", ),
    size: int = Query(PAGE_SIZE, description="Size", ),
     */
    return this._httpClient.post<any>(`${environment.api}/search`, formData, this.httpOptions);
  }
}
