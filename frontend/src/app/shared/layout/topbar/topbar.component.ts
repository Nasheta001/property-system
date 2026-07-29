import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';
import { OrgSwitcherComponent } from '../../ui/org-switcher/org-switcher.component';
import { ThemeToggleComponent } from '../../ui/theme-toggle/theme-toggle.component';

@Component({
  selector: 'app-topbar',
  imports: [MatButtonModule, MatIconModule, MatMenuModule, OrgSwitcherComponent, ThemeToggleComponent],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss',
})
export class TopbarComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly currentUser = this.authService.currentUser;

  logout(): void {
    this.authService.logout().subscribe(() => this.router.navigate(['/auth/login']));
  }

  initials(): string {
    const user = this.currentUser();
    if (!user) return '';
    const first = user.first_name?.[0] ?? user.email[0];
    const last = user.last_name?.[0] ?? '';
    return (first + last).toUpperCase();
  }
}
