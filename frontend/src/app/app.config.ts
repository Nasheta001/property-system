import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  ApplicationConfig,
  inject,
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
  provideZoneChangeDetection,
} from '@angular/core';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { AuthService } from './core/services/auth.service';
import { OrganizationService } from './core/services/organization.service';

async function bootstrapSession(): Promise<void> {
  const authService = inject(AuthService);
  const organizationService = inject(OrganizationService);

  if (!authService.hasStoredSession()) {
    authService.isBootstrapping.set(false);
    return;
  }

  try {
    await firstValueFrom(authService.bootstrap());
    await firstValueFrom(organizationService.loadOrganizations());
  } catch {
    // Stored token is invalid/expired — the user simply lands on the
    // public routes and can sign in again; the interceptor already clears
    // storage on the first 401 a real request would otherwise produce.
  } finally {
    authService.isBootstrapping.set(false);
  }
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
    provideAppInitializer(bootstrapSession),
  ],
};
