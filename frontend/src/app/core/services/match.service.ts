import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpParams } from '@angular/common/http';
import { BaseService } from './base.service';
import { 
  Match, 
  MatchCreate, 
  MatchUpdate, 
  MatchStatus, 
  TossInfo,
  PaginatedResponse 
} from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class MatchService extends BaseService<Match, MatchCreate, MatchUpdate> {
  constructor() {
    super();
    this.endpoint = 'matches';
  }

  getLiveMatches(params?: any): Observable<PaginatedResponse<Match>> {
    return this.http.get<PaginatedResponse<Match>>(this.getUrl('/live'), { params: this.buildParams(params) });
  }

  filterByStatus(status: MatchStatus, params?: any): Observable<PaginatedResponse<Match>> {
    return this.getAll({ ...params, status });
  }

  filterByTournament(tournamentId: number, params?: any): Observable<PaginatedResponse<Match>> {
    return this.getAll({ ...params, tournament_id: tournamentId });
  }

  filterByVenue(venueId: number, params?: any): Observable<PaginatedResponse<Match>> {
    return this.getAll({ ...params, venue_id: venueId });
  }

  updateMatchStatus(matchId: string, status: MatchStatus): Observable<Match> {
    return this.http.patch<Match>(this.getUrl(`/${matchId}/status`), { status });
  }

  setMatchToss(matchId: string, tossInfo: TossInfo): Observable<Match> {
    return this.http.post<Match>(this.getUrl(`/${matchId}/toss`), tossInfo);
  }

  setMatchResult(matchId: string, result: { result: string; winner_team_id?: number }): Observable<Match> {
    return this.http.patch<Match>(this.getUrl(`/${matchId}`), result);
  }

  private buildParams(params?: any): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return httpParams;
  }
}
