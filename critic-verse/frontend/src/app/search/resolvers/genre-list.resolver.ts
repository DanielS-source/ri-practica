import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { SearchService } from '../search.service';

@Injectable({
    providedIn: 'root',
})
export class GenreListResolver implements Resolve<any> {
    /**
     * Constructor
     */
    constructor(
        private _searchService: SearchService,
        private _router: Router) { }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Resolver
     *
     * @param route
     * @param state
     */
    resolve(route: ActivatedRouteSnapshot): Observable<any> {
        return this._searchService.getGenreList().pipe(
            catchError((error) => {
                console.error(error);
                // Throw notification
                return throwError(error);
            }),
        );
    }
}
