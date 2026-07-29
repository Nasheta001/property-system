import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { DocumentType, PropertyDocument } from '../models/document.model';
import { PaginatedResponse } from '../models/property.model';

export interface DocumentUploadPayload {
  title: string;
  description?: string;
  document_type: DocumentType;
  property?: string;
  lease?: string;
  tenant?: string;
  file: File;
}

@Injectable({ providedIn: 'root' })
export class DocumentsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/documents/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<PropertyDocument>> {
    return this.http.get<PaginatedResponse<PropertyDocument>>(this.baseUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  upload(payload: DocumentUploadPayload): Observable<PropertyDocument> {
    const formData = new FormData();
    formData.append('title', payload.title);
    formData.append('document_type', payload.document_type);
    if (payload.description) formData.append('description', payload.description);
    if (payload.property) formData.append('property', payload.property);
    if (payload.lease) formData.append('lease', payload.lease);
    if (payload.tenant) formData.append('tenant', payload.tenant);
    formData.append('file', payload.file);
    return this.http.post<PropertyDocument>(this.baseUrl, formData);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${id}/`);
  }
}
