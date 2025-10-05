import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { Team, TeamCreate, TeamUpdate, TeamSummary, PaginatedResponse } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class TeamService extends BaseService<Team, TeamCreate, TeamUpdate> {
  constructor() {
    super();
    this.endpoint = 'teams';
  }

  searchByCountry(countryCode: string, params?: any): Observable<PaginatedResponse<Team>> {
    return this.search('', { ...params, country_code: countryCode });
  }

  getTeamRoster(teamId: string): Observable<any> {
    return this.http.get<any>(this.getUrl(`/${teamId}/roster`));
  }
}
