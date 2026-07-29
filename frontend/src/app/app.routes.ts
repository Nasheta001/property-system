import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { guestGuard } from './core/guards/guest.guard';
import { platformStaffGuard } from './core/guards/platform-staff.guard';

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
      {
        path: 'properties',
        loadComponent: () =>
          import('./features/properties/properties-page.component').then((m) => m.PropertiesPageComponent),
      },
      {
        path: 'tenants',
        loadComponent: () =>
          import('./features/tenants/tenants-page.component').then((m) => m.TenantsPageComponent),
      },
      {
        path: 'leases',
        loadComponent: () =>
          import('./features/leases/leases-page.component').then((m) => m.LeasesPageComponent),
      },
      {
        path: 'payments',
        loadComponent: () =>
          import('./features/payments/payments-page.component').then((m) => m.PaymentsPageComponent),
      },
      {
        path: 'maintenance',
        loadComponent: () =>
          import('./features/maintenance/maintenance-page.component').then((m) => m.MaintenancePageComponent),
      },
      {
        path: 'vendors',
        loadComponent: () =>
          import('./features/maintenance/vendors-page.component').then((m) => m.VendorsPageComponent),
      },
      {
        path: 'documents',
        loadComponent: () =>
          import('./features/documents/documents-page.component').then((m) => m.DocumentsPageComponent),
      },
      {
        path: 'activity',
        loadComponent: () =>
          import('./features/activity/activity-page.component').then((m) => m.ActivityPageComponent),
      },
      {
        path: 'reports',
        loadComponent: () =>
          import('./features/reports/reports-page.component').then((m) => m.ReportsPageComponent),
      },
      {
        path: 'support',
        loadComponent: () =>
          import('./features/support/support-page.component').then((m) => m.SupportPageComponent),
      },
      {
        path: 'calendar',
        loadComponent: () =>
          import('./features/calendar/calendar-page.component').then((m) => m.CalendarPageComponent),
      },
      {
        path: 'subscription',
        loadComponent: () =>
          import('./features/subscriptions/subscription-page.component').then(
            (m) => m.SubscriptionPageComponent
          ),
      },
      {
        path: 'admin',
        canActivate: [platformStaffGuard],
        loadComponent: () => import('./features/admin/admin-page.component').then((m) => m.AdminPageComponent),
      },
      {
        path: 'assistant',
        loadComponent: () =>
          import('./features/assistant/assistant-page.component').then((m) => m.AssistantPageComponent),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
