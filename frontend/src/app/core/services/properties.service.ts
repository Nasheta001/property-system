import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse, Property, Unit } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class PropertiesService {
  private readonly http = inject(HttpClient);

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Property>> {
    return this.http.get<PaginatedResponse<Property>>(`${environment.apiUrl}/properties/`, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  listUnits(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Unit>> {
    return this.http.get<PaginatedResponse<Unit>>(`${environment.apiUrl}/units/`, {
      params: new HttpParams({ fromObject: params }),
    });
  }
}
