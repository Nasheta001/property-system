import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/property.model';
import { TenantProfile, TenantProfilePayload } from '../models/tenant.model';

@Injectable({ providedIn: 'root' })
export class TenantsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/tenants/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<TenantProfile>> {
    return this.http.get<PaginatedResponse<TenantProfile>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  create(payload: Partial<TenantProfilePayload>): Observable<TenantProfile> {
    return this.http.post<TenantProfile>(this.baseUrl, payload);
  }

  update(id: string, payload: Partial<TenantProfilePayload>): Observable<TenantProfile> {
    return this.http.patch<TenantProfile>(`${this.baseUrl}${id}/`, payload);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${id}/`);
  }
}
