import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  Building,
  BuildingPayload,
  Floor,
  FloorPayload,
  PaginatedResponse,
  Property,
  PropertyPayload,
  Unit,
  UnitPayload,
} from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class PropertiesService {
  private readonly http = inject(HttpClient);
  private readonly propertiesUrl = `${environment.apiUrl}/properties/`;
  private readonly buildingsUrl = `${environment.apiUrl}/buildings/`;
  private readonly floorsUrl = `${environment.apiUrl}/floors/`;
  private readonly unitsUrl = `${environment.apiUrl}/units/`;

  list(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Property>> {
    return this.http.get<PaginatedResponse<Property>>(this.propertiesUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createProperty(payload: Partial<PropertyPayload>): Observable<Property> {
    return this.http.post<Property>(this.propertiesUrl, payload);
  }

  updateProperty(id: string, payload: Partial<PropertyPayload>): Observable<Property> {
    return this.http.patch<Property>(`${this.propertiesUrl}${id}/`, payload);
  }

  deleteProperty(id: string): Observable<void> {
    return this.http.delete<void>(`${this.propertiesUrl}${id}/`);
  }

  listBuildings(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Building>> {
    return this.http.get<PaginatedResponse<Building>>(this.buildingsUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createBuilding(payload: BuildingPayload): Observable<Building> {
    return this.http.post<Building>(this.buildingsUrl, payload);
  }

  updateBuilding(id: string, payload: Partial<BuildingPayload>): Observable<Building> {
    return this.http.patch<Building>(`${this.buildingsUrl}${id}/`, payload);
  }

  deleteBuilding(id: string): Observable<void> {
    return this.http.delete<void>(`${this.buildingsUrl}${id}/`);
  }

  listFloors(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Floor>> {
    return this.http.get<PaginatedResponse<Floor>>(this.floorsUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createFloor(payload: FloorPayload): Observable<Floor> {
    return this.http.post<Floor>(this.floorsUrl, payload);
  }

  updateFloor(id: string, payload: Partial<FloorPayload>): Observable<Floor> {
    return this.http.patch<Floor>(`${this.floorsUrl}${id}/`, payload);
  }

  deleteFloor(id: string): Observable<void> {
    return this.http.delete<void>(`${this.floorsUrl}${id}/`);
  }

  listUnits(params: Record<string, string | number> = {}): Observable<PaginatedResponse<Unit>> {
    return this.http.get<PaginatedResponse<Unit>>(this.unitsUrl, {
      params: new HttpParams({ fromObject: params }),
    });
  }

  createUnit(payload: UnitPayload): Observable<Unit> {
    return this.http.post<Unit>(this.unitsUrl, payload);
  }

  updateUnit(id: string, payload: Partial<UnitPayload>): Observable<Unit> {
    return this.http.patch<Unit>(`${this.unitsUrl}${id}/`, payload);
  }

  deleteUnit(id: string): Observable<void> {
    return this.http.delete<void>(`${this.unitsUrl}${id}/`);
  }
}
