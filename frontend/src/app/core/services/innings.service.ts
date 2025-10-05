import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { 
  Innings, 
  InningsCreate, 
  InningsUpdate, 
  InningsScore, 
  Partnership 
} from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class InningsService extends BaseService<Innings, InningsCreate, InningsUpdate> {
  constructor() {
    super();
    this.endpoint = 'innings';
  }

  getInningsScore(inningsId: string): Observable<InningsScore> {
    return this.http.get<InningsScore>(this.getUrl(`/${inningsId}/score`));
  }

  getCurrentPartnership(inningsId: string): Observable<Partnership> {
    return this.http.get<Partnership>(this.getUrl(`/${inningsId}/partnership`));
  }

  closeInnings(inningsId: string, reason: 'DECLARED' | 'FORFEITED'): Observable<Innings> {
    return this.http.post<Innings>(this.getUrl(`/${inningsId}/close`), { reason });
  }
}
