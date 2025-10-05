import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';
import { 
  Delivery, 
  DeliveryCreate,
  BallByBallRequest,
  BatsmanStats,
  BowlerStats,
  WagonWheelData,
  PitchMapData 
} from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class DeliveryService extends BaseService<Delivery, DeliveryCreate, any> {
  constructor() {
    super();
    this.endpoint = 'deliveries';
  }

  recordBallByBall(data: BallByBallRequest): Observable<Delivery> {
    return this.http.post<Delivery>(this.getUrl('/ball-by-ball'), data);
  }

  getOverSummary(inningsId: string, overNumber: number): Observable<Delivery[]> {
    return this.http.get<Delivery[]>(this.getUrl(`/innings/${inningsId}/over/${overNumber}`));
  }

  getBatsmanStats(inningsId: string, batsmanId: string): Observable<BatsmanStats> {
    return this.http.get<BatsmanStats>(this.getUrl(`/innings/${inningsId}/batsman/${batsmanId}/stats`));
  }

  getBowlerStats(inningsId: string, bowlerId: string): Observable<BowlerStats> {
    return this.http.get<BowlerStats>(this.getUrl(`/innings/${inningsId}/bowler/${bowlerId}/stats`));
  }

  getWagonWheelData(inningsId: string, batsmanId?: string): Observable<WagonWheelData> {
    const url = batsmanId 
      ? this.getUrl(`/innings/${inningsId}/batsman/${batsmanId}/wagon-wheel`)
      : this.getUrl(`/innings/${inningsId}/wagon-wheel`);
    return this.http.get<WagonWheelData>(url);
  }

  getPitchMapData(inningsId: string, bowlerId?: string): Observable<PitchMapData> {
    const url = bowlerId
      ? this.getUrl(`/innings/${inningsId}/bowler/${bowlerId}/pitch-map`)
      : this.getUrl(`/innings/${inningsId}/pitch-map`);
    return this.http.get<PitchMapData>(url);
  }

  correctDelivery(deliveryId: string, data: Partial<DeliveryCreate>): Observable<Delivery> {
    return this.http.post<Delivery>(this.getUrl(`/${deliveryId}/correct`), data);
  }
}
