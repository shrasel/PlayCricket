import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { Player, PlayerCreate, PlayerUpdate, BattingStyle, BowlingStyle, PaginatedResponse } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class PlayerService extends BaseService<Player, PlayerCreate, PlayerUpdate> {
  constructor() {
    super();
    this.endpoint = 'players';
  }

  filterByBattingStyle(style: BattingStyle, params?: any): Observable<PaginatedResponse<Player>> {
    return this.getAll({ ...params, batting_style: style });
  }

  filterByBowlingStyle(style: BowlingStyle, params?: any): Observable<PaginatedResponse<Player>> {
    return this.getAll({ ...params, bowling_style: style });
  }

  filterByAgeRange(minAge?: number, maxAge?: number, params?: any): Observable<PaginatedResponse<Player>> {
    return this.getAll({ ...params, min_age: minAge, max_age: maxAge });
  }
}
