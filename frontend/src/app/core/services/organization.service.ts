import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Organization } from '../models/organization.model';
import { PaginatedResponse } from '../models/property.model';
import { TokenStorageService } from './token-storage.service';

@Injectable({ providedIn: 'root' })
export class OrganizationService {
  private readonly http = inject(HttpClient);
  private readonly tokenStorage = inject(TokenStorageService);

  private readonly baseUrl = `${environment.apiUrl}/organizations/`;

  readonly organizations = signal<Organization[]>([]);
  readonly activeOrganizationId = signal<string | null>(this.tokenStorage.getActiveOrganizationId());
  readonly activeOrganization = computed(
    () => this.organizations().find((org) => org.id === this.activeOrganizationId()) ?? null
  );

  loadOrganizations(): Observable<PaginatedResponse<Organization>> {
    return this.http.get<PaginatedResponse<Organization>>(this.baseUrl).pipe(
      tap((response) => {
        this.organizations.set(response.results);
        const activeId = this.activeOrganizationId();
        const stillValid = activeId && response.results.some((org) => org.id === activeId);
        if (!stillValid && response.results.length > 0) {
          this.setActiveOrganization(response.results[0].id);
        }
      })
    );
  }

  setActiveOrganization(organizationId: string): void {
    this.activeOrganizationId.set(organizationId);
    this.tokenStorage.setActiveOrganizationId(organizationId);
  }

  createOrganization(payload: Partial<Organization>): Observable<Organization> {
    return this.http
      .post<Organization>(this.baseUrl, payload)
      .pipe(tap((organization) => this.organizations.update((orgs) => [...orgs, organization])));
  }
}
