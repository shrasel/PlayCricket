import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { Tournament, TournamentCreate, TournamentUpdate, MatchType, PaginatedResponse } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class TournamentService extends BaseService<Tournament, TournamentCreate, TournamentUpdate> {
  constructor() {
    super();
    this.endpoint = 'tournaments';
  }

  filterByMatchType(matchType: MatchType, params?: any): Observable<PaginatedResponse<Tournament>> {
    return this.getAll({ ...params, match_type: matchType });
  }

  getActiveTournaments(params?: any): Observable<PaginatedResponse<Tournament>> {
    return this.getAll({ ...params, active: true });
  }

  getUpcomingTournaments(params?: any): Observable<PaginatedResponse<Tournament>> {
    return this.getAll({ ...params, upcoming: true });
  }
}
