import { Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive } from '@angular/router';

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
  ];
}
