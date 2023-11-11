import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';
import { GameItem, GameQuery, IPData, SearchItem, SuggestionQuery } from './search.model';

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

    getSuggestions(query: SuggestionQuery): Observable<any> {
        return this._httpClient.post<any>(`${environment.api}/suggestions`, query, this.httpOptions);
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

    getContinent(): Observable<IPData> {
        return this._httpClient.get<IPData>(`${environment.ipApi}`, this.httpOptions)
            .pipe(
                map((response: any) => {
                    return {
                        ip: response.ip,
                        network: response.network,
                        version: response.version,
                        city: response.city,
                        region: response.region,
                        regionCode: response.region_code,
                        country: response.country,
                        countryName: response.country_name,
                        countryCode: response.country_code,
                        countryCodeIso: response.country_code_iso3,
                        countryCapital: response.country_capital,
                        countryTld: response.country_tld,
                        continentName: this.parseContinentCode(response.continent_code),
                        continentCode: response.continent_code,
                        inEU: response.in_eu,
                        postalCode: response.postal,
                        geolocation: {
                            latitude: response.latitude,
                            longitude: response.longitude
                        },
                        timeZone: response.timezone,
                        utcOffset: response.utc_offset,
                        countryCallingCode: response.country_calling_code,
                        currency: response.currency,
                        currencyName: response.currency_name,
                        languages: response.languages.split(","),
                        countryArea: response.country_area,
                        countryPopulation: response.country_population,
                        asn: response.asn,
                        org: response.org
                    };
                })
            );
    }

    parseContinentCode(cCode: string): string {
        switch (cCode) {
            default:
            case 'EU':
                return "Europe";
            case 'NA':
                return "North America";
            case 'AN':
                return "Antarctica";
            case 'OC':
                return "Oceania";
            case 'SA':
                return "South America"; 
            case 'AF':
                return "Africa";
            case 'AS':
                return "Asia";
        }
    }
}
