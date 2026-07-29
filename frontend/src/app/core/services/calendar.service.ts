import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CalendarEventsResponse } from '../models/calendar.model';

@Injectable({ providedIn: 'root' })
export class CalendarService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/calendar`;

  getEvents(start: string, end: string): Observable<CalendarEventsResponse> {
    return this.http.get<CalendarEventsResponse>(`${this.baseUrl}/events/`, {
      params: new HttpParams({ fromObject: { start, end } }),
    });
  }
}
