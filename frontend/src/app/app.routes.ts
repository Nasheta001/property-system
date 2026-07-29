import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { guestGuard } from './core/guards/guest.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./shared/layout/public-layout/public-layout.component').then((m) => m.PublicLayoutComponent),
    children: [
      {
        path: '',
        loadComponent: () => import('./features/landing/landing-page.component').then((m) => m.LandingPageComponent),
      },
      {
        path: 'auth',
        canActivate: [guestGuard],
        children: [
          {
            path: 'login',
            loadComponent: () =>
              import('./features/auth/login/login-page.component').then((m) => m.LoginPageComponent),
          },
          {
            path: 'register',
            loadComponent: () =>
              import('./features/auth/register/register-page.component').then((m) => m.RegisterPageComponent),
          },
          { path: '', redirectTo: 'login', pathMatch: 'full' },
        ],
      },
    ],
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./shared/layout/dashboard-layout/dashboard-layout.component').then(
        (m) => m.DashboardLayoutComponent
      ),
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
