import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ActivityLogEntry } from '../models/activity.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class ActivityService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/activity/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<ActivityLogEntry>> {
    return this.http.get<PaginatedResponse<ActivityLogEntry>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }
}
