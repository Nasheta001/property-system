import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandlerFn,
  HttpInterceptorFn,
  HttpRequest,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';
import { OrganizationService } from '../services/organization.service';
import { TokenStorageService } from '../services/token-storage.service';

const AUTH_ENDPOINTS_WITHOUT_TOKEN = ['/auth/login/', '/auth/register/', '/auth/refresh/'];

/**
 * Attaches the JWT access token and the caller's active organization to
 * every request against our own API, and transparently refreshes an
 * expired access token once before giving up and forcing a re-login.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const tokenStorage = inject(TokenStorageService);
  const organizationService = inject(OrganizationService);
  const router = inject(Router);

  if (!req.url.startsWith(environment.apiUrl)) {
    return next(req);
  }

  const isAuthEndpoint = AUTH_ENDPOINTS_WITHOUT_TOKEN.some((path) => req.url.includes(path));
  const accessToken = tokenStorage.getAccessToken();
  const activeOrganizationId = organizationService.activeOrganizationId();
  const authedReq = withAuthHeaders(req, isAuthEndpoint ? null : accessToken, activeOrganizationId);

  return next(authedReq).pipe(
    catchError((error: unknown) => {
      if (
        error instanceof HttpErrorResponse &&
        error.status === 401 &&
        !isAuthEndpoint &&
        tokenStorage.getRefreshToken()
      ) {
        return refreshAccessToken(req, next, tokenStorage, activeOrganizationId, router);
      }
      if (error instanceof HttpErrorResponse && error.status === 401) {
        tokenStorage.clear();
        router.navigate(['/auth/login']);
      }
      return throwError(() => error);
    })
  );
};

function withAuthHeaders(
  req: HttpRequest<unknown>,
  accessToken: string | null,
  activeOrganizationId: string | null
): HttpRequest<unknown> {
  const headers: Record<string, string> = {};
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  if (activeOrganizationId) {
    headers['X-Organization-ID'] = activeOrganizationId;
  }
  return Object.keys(headers).length > 0 ? req.clone({ setHeaders: headers }) : req;
}

function refreshAccessToken(
  originalReq: HttpRequest<unknown>,
  next: HttpHandlerFn,
  tokenStorage: TokenStorageService,
  activeOrganizationId: string | null,
  router: Router
): Observable<HttpEvent<unknown>> {
  const refresh = tokenStorage.getRefreshToken();

  return new Observable<HttpEvent<unknown>>((subscriber) => {
    fetch(`${environment.apiUrl}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Unable to refresh session.');
        }
        return res.json();
      })
      .then((data: { access: string }) => {
        tokenStorage.setAccessToken(data.access);
        const retriedReq = withAuthHeaders(originalReq, data.access, activeOrganizationId);
        next(retriedReq).subscribe(subscriber);
      })
      .catch((err) => {
        tokenStorage.clear();
        router.navigate(['/auth/login']);
        subscriber.error(err);
      });
  });
}
