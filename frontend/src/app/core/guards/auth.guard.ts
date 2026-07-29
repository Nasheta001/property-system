import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from '../services/auth.service';

/**
 * Session state is hydrated once at app bootstrap (see `app.config.ts`)
 * before the router activates any route, so by the time a guard runs,
 * `currentUser` reliably reflects whether the stored token is valid.
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isAuthenticated() ? true : router.createUrlTree(['/auth/login']);
};
