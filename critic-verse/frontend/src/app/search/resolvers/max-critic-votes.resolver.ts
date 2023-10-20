import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { SearchService } from '../search.service';

@Injectable({
    providedIn: 'root',
})
export class MaxCriticVotesResolver implements Resolve<any> {
    /**
     * Constructor
     */
    constructor(
        private _searchSerice: SearchService,
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
        return this._searchSerice.getMaxCriticVotes().pipe(
            catchError((error) => {
                console.error(error);
                // Throw notification
                return throwError(error);
            }),
        );
    }
}