import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LedgerEntry, Payment, PaymentCreatePayload } from '../models/payment.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class PaymentsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/payments/`;
  private readonly ledgerUrl = `${environment.apiUrl}/ledger-entries/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Payment>> {
    return this.http.get<PaginatedResponse<Payment>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  create(payload: PaymentCreatePayload): Observable<Payment> {
    return this.http.post<Payment>(this.baseUrl, payload);
  }

  markPaid(id: string, providerReference = ''): Observable<Payment> {
    return this.http.post<Payment>(`${this.baseUrl}${id}/mark_paid/`, { provider_reference: providerReference });
  }

  markFailed(id: string, reason: string): Observable<Payment> {
    return this.http.post<Payment>(`${this.baseUrl}${id}/mark_failed/`, { reason });
  }

  cancel(id: string): Observable<Payment> {
    return this.http.post<Payment>(`${this.baseUrl}${id}/cancel/`, {});
  }

  refund(id: string, reason: string): Observable<Payment> {
    return this.http.post<Payment>(`${this.baseUrl}${id}/refund/`, { reason });
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${id}/`);
  }

  listLedgerEntries(params: Record<string, string | number> = {}): Observable<PaginatedResponse<LedgerEntry>> {
    return this.http.get<PaginatedResponse<LedgerEntry>>(this.ledgerUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }
}
