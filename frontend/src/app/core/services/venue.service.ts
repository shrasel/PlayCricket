import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { Venue, VenueCreate, VenueUpdate, PaginatedResponse } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class VenueService extends BaseService<Venue, VenueCreate, VenueUpdate> {
  constructor() {
    super();
    this.endpoint = 'venues';
  }

  filterByCity(city: string, params?: any): Observable<PaginatedResponse<Venue>> {
    return this.getAll({ ...params, city });
  }

  filterByCountry(countryCode: string, params?: any): Observable<PaginatedResponse<Venue>> {
    return this.getAll({ ...params, country_code: countryCode });
  }
}
