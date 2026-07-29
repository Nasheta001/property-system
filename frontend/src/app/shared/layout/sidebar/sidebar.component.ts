import { Component, computed, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-sidebar',
  imports: [RouterLink, RouterLinkActive, MatIconModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  private readonly authService = inject(AuthService);

  protected readonly isPlatformStaff = computed(() => !!this.authService.currentUser()?.is_staff);

  protected readonly navItems: NavItem[] = [
    { label: 'Dashboard', icon: 'space_dashboard', route: '/dashboard' },
    { label: 'Properties', icon: 'apartment', route: '/properties' },
    { label: 'Tenants', icon: 'groups', route: '/tenants' },
    { label: 'Leases', icon: 'description', route: '/leases' },
    { label: 'Payments', icon: 'payments', route: '/payments' },
    { label: 'Maintenance', icon: 'build', route: '/maintenance' },
    { label: 'Vendors', icon: 'handyman', route: '/vendors' },
    { label: 'Documents', icon: 'folder', route: '/documents' },
    { label: 'Activity', icon: 'history', route: '/activity' },
    { label: 'Reports', icon: 'bar_chart', route: '/reports' },
    { label: 'Support', icon: 'support_agent', route: '/support' },
    { label: 'Calendar', icon: 'calendar_month', route: '/calendar' },
    { label: 'Subscription', icon: 'workspace_premium', route: '/subscription' },
    { label: 'Assistant', icon: 'auto_awesome', route: '/assistant' },
    { label: 'Maps', icon: 'map', route: '/maps' },
  ];

  protected readonly platformNavItems: NavItem[] = [
    { label: 'Admin Portal', icon: 'admin_panel_settings', route: '/admin' },
  ];
}
