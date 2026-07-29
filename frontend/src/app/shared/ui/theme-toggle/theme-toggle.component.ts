import { Component, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';

import { ThemePreference, ThemeService } from '../../../core/services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  imports: [MatIconModule, MatMenuModule, MatButtonModule],
  templateUrl: './theme-toggle.component.html',
  styleUrl: './theme-toggle.component.scss',
})
export class ThemeToggleComponent {
  protected readonly themeService = inject(ThemeService);

  protected readonly icons: Record<ThemePreference, string> = {
    light: 'light_mode',
    dark: 'dark_mode',
    system: 'brightness_auto',
  };

  select(preference: ThemePreference): void {
    this.themeService.setPreference(preference);
  }
}
