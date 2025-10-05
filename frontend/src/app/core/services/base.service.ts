import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { PaginatedResponse } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class BaseService<T, TCreate, TUpdate> {
  protected http = inject(HttpClient);
  protected baseUrl = environment.apiUrl;
  protected endpoint!: string;

  protected getUrl(path: string = ''): string {
    return `${this.baseUrl}/${this.endpoint}${path}`;
  }

  getAll(params?: { page?: number; page_size?: number; [key: string]: any }): Observable<PaginatedResponse<T>> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<PaginatedResponse<T>>(this.getUrl(), { params: httpParams });
  }

  getById(id: string): Observable<T> {
    return this.http.get<T>(this.getUrl(`/${id}`));
  }

  create(data: TCreate): Observable<T> {
    return this.http.post<T>(this.getUrl(), data);
  }

  update(id: string, data: TUpdate): Observable<T> {
    return this.http.patch<T>(this.getUrl(`/${id}`), data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(this.getUrl(`/${id}`));
  }

  search(query: string, params?: any): Observable<PaginatedResponse<T>> {
    let httpParams = new HttpParams().set('q', query);
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<PaginatedResponse<T>>(this.getUrl(), { params: httpParams });
  }
}
