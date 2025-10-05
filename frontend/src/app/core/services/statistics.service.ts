import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { Scorecard, CareerStats, MatchSummary } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class StatisticsService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/stats`;

  getMatchScorecard(matchId: string): Observable<Scorecard> {
    return this.http.get<Scorecard>(`${this.baseUrl}/matches/${matchId}/scorecard`);
  }

  getPlayerCareerStats(playerId: string): Observable<CareerStats> {
    return this.http.get<CareerStats>(`${this.baseUrl}/players/${playerId}/career`);
  }

  getMatchSummary(matchId: string): Observable<MatchSummary> {
    return this.http.get<MatchSummary>(`${this.baseUrl}/matches/${matchId}/summary`);
  }
}
