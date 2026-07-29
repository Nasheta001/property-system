import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Lease, LeaseCreatePayload } from '../models/lease.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class LeasesService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/leases/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Lease>> {
    return this.http.get<PaginatedResponse<Lease>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  create(payload: LeaseCreatePayload): Observable<Lease> {
    return this.http.post<Lease>(this.baseUrl, payload);
  }

  activate(id: string): Observable<Lease> {
    return this.http.post<Lease>(`${this.baseUrl}${id}/activate/`, {});
  }

  terminate(id: string, reason: string): Observable<Lease> {
    return this.http.post<Lease>(`${this.baseUrl}${id}/terminate/`, { reason });
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${id}/`);
  }
}
