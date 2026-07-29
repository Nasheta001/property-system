import { Injectable } from '@angular/core';

const ACCESS_TOKEN_KEY = 'ps_access_token';
const REFRESH_TOKEN_KEY = 'ps_refresh_token';
const ACTIVE_ORG_KEY = 'ps_active_organization_id';

/**
 * Thin wrapper around localStorage. Kept as its own service (rather than
 * calling localStorage directly from AuthService) so token persistence can
 * be swapped for a more secure strategy (e.g. httpOnly cookies issued by a
 * BFF) without touching call sites.
 */
@Injectable({ providedIn: 'root' })
export class TokenStorageService {
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  setTokens(access: string, refresh: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }

  setAccessToken(access: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
  }

  clear(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(ACTIVE_ORG_KEY);
  }

  getActiveOrganizationId(): string | null {
    return localStorage.getItem(ACTIVE_ORG_KEY);
  }

  setActiveOrganizationId(organizationId: string): void {
    localStorage.setItem(ACTIVE_ORG_KEY, organizationId);
  }
}
