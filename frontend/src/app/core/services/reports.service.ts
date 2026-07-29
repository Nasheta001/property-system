import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  LeaseExpirationRow,
  MaintenanceReport,
  OccupancyReportRow,
  RevenueReportPoint,
} from '../models/report.model';

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/reports`;

  revenue(months = 6): Observable<RevenueReportPoint[]> {
    return this.http.get<RevenueReportPoint[]>(`${this.baseUrl}/revenue/`, {
      params: new HttpParams({ fromObject: { months } }),
    });
  }

  occupancy(): Observable<OccupancyReportRow[]> {
    return this.http.get<OccupancyReportRow[]>(`${this.baseUrl}/occupancy/`);
  }

  maintenance(): Observable<MaintenanceReport> {
    return this.http.get<MaintenanceReport>(`${this.baseUrl}/maintenance/`);
  }

  leaseExpirations(): Observable<LeaseExpirationRow[]> {
    return this.http.get<LeaseExpirationRow[]>(`${this.baseUrl}/lease-expirations/`);
  }
}
