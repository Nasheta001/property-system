import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AppNotification } from '../models/notification.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class NotificationsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/notifications/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<AppNotification>> {
    return this.http.get<PaginatedResponse<AppNotification>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  unreadCount(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(`${this.baseUrl}unread-count/`);
  }

  markRead(id: string): Observable<AppNotification> {
    return this.http.post<AppNotification>(`${this.baseUrl}${id}/mark_read/`, {});
  }

  markAllRead(): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.baseUrl}mark-all-read/`, {});
  }
}
