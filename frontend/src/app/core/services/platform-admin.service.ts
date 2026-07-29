import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/property.model';
import { PlatformOrganization, PlatformStats } from '../models/platform.model';

@Injectable({ providedIn: 'root' })
export class PlatformAdminService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/platform`;

  getStats(): Observable<PlatformStats> {
    return this.http.get<PlatformStats>(`${this.baseUrl}/stats/`);
  }

  listOrganizations(): Observable<PaginatedResponse<PlatformOrganization>> {
    return this.http.get<PaginatedResponse<PlatformOrganization>>(`${this.baseUrl}/organizations/`, {
      params: { page_size: 100 },
    });
  }

  suspend(id: string, reason: string): Observable<PlatformOrganization> {
    return this.http.post<PlatformOrganization>(`${this.baseUrl}/organizations/${id}/suspend/`, { reason });
  }

  reactivate(id: string): Observable<PlatformOrganization> {
    return this.http.post<PlatformOrganization>(`${this.baseUrl}/organizations/${id}/reactivate/`, {});
  }
}
