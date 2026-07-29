import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  MaintenanceAttachment,
  MaintenanceComment,
  MaintenanceRequest,
  MaintenanceRequestPayload,
  Vendor,
  VendorPayload,
} from '../models/maintenance.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class MaintenanceService {
  private readonly http = inject(HttpClient);
  private readonly requestsUrl = `${environment.apiUrl}/maintenance-requests/`;
  private readonly vendorsUrl = `${environment.apiUrl}/vendors/`;

  listRequests(params: Record<string, string | number> = {}): Observable<PaginatedResponse<MaintenanceRequest>> {
    return this.http.get<PaginatedResponse<MaintenanceRequest>>(this.requestsUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createRequest(payload: MaintenanceRequestPayload): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(this.requestsUrl, payload);
  }

  verify(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/verify/`, {});
  }

  assign(id: string, vendor: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/assign/`, { vendor });
  }

  accept(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/accept/`, {});
  }

  startProgress(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/start-progress/`, {});
  }

  waitForParts(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/wait-for-parts/`, {});
  }

  complete(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/complete/`, {});
  }

  review(id: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/review/`, {});
  }

  close(id: string, closureNotes: string): Observable<MaintenanceRequest> {
    return this.http.post<MaintenanceRequest>(`${this.requestsUrl}${id}/close/`, { closure_notes: closureNotes });
  }

  deleteRequest(id: string): Observable<void> {
    return this.http.delete<void>(`${this.requestsUrl}${id}/`);
  }

  listComments(requestId: string): Observable<MaintenanceComment[]> {
    return this.http.get<MaintenanceComment[]>(`${this.requestsUrl}${requestId}/comments/`);
  }

  addComment(requestId: string, body: string): Observable<MaintenanceComment> {
    return this.http.post<MaintenanceComment>(`${this.requestsUrl}${requestId}/comments/`, { body });
  }

  listAttachments(requestId: string): Observable<MaintenanceAttachment[]> {
    return this.http.get<MaintenanceAttachment[]>(`${this.requestsUrl}${requestId}/attachments/`);
  }

  uploadAttachment(requestId: string, file: File, caption: string): Observable<MaintenanceAttachment> {
    const formData = new FormData();
    formData.append('file', file);
    if (caption) {
      formData.append('caption', caption);
    }
    return this.http.post<MaintenanceAttachment>(`${this.requestsUrl}${requestId}/attachments/`, formData);
  }

  listVendors(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Vendor>> {
    return this.http.get<PaginatedResponse<Vendor>>(this.vendorsUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createVendor(payload: Partial<VendorPayload>): Observable<Vendor> {
    return this.http.post<Vendor>(this.vendorsUrl, payload);
  }

  updateVendor(id: string, payload: Partial<VendorPayload>): Observable<Vendor> {
    return this.http.patch<Vendor>(`${this.vendorsUrl}${id}/`, payload);
  }

  deleteVendor(id: string): Observable<void> {
    return this.http.delete<void>(`${this.vendorsUrl}${id}/`);
  }
}
