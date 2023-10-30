import { Injectable } from "@angular/core";
import { Resolve, Router, ActivatedRouteSnapshot } from "@angular/router";
import { Observable, catchError, throwError } from "rxjs";
import { SearchService } from "../search.service";

@Injectable({
    providedIn: 'root',
})
export class PlatformListResolver implements Resolve<any> {
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
        return this._searchSerice.getPlatformList().pipe(
            catchError((error) => {
                console.error(error);
                // Throw notification
                return throwError(error);
            }),
        );
    }
}
