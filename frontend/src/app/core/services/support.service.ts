import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/property.model';
import { SupportTicket, SupportTicketComment, SupportTicketPayload } from '../models/support.model';

@Injectable({ providedIn: 'root' })
export class SupportService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/support-tickets/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<SupportTicket>> {
    return this.http.get<PaginatedResponse<SupportTicket>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  create(payload: SupportTicketPayload): Observable<SupportTicket> {
    return this.http.post<SupportTicket>(this.baseUrl, payload);
  }

  close(id: string): Observable<SupportTicket> {
    return this.http.post<SupportTicket>(`${this.baseUrl}${id}/close/`, {});
  }

  reopen(id: string): Observable<SupportTicket> {
    return this.http.post<SupportTicket>(`${this.baseUrl}${id}/reopen/`, {});
  }

  listComments(ticketId: string): Observable<SupportTicketComment[]> {
    return this.http.get<SupportTicketComment[]>(`${this.baseUrl}${ticketId}/comments/`);
  }

  addComment(ticketId: string, body: string): Observable<SupportTicketComment> {
    return this.http.post<SupportTicketComment>(`${this.baseUrl}${ticketId}/comments/`, { body });
  }
}
