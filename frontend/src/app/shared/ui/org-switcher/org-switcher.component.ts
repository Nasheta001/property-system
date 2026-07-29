import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';

import { OrganizationService } from '../../../core/services/organization.service';

@Component({
  selector: 'app-org-switcher',
  imports: [MatButtonModule, MatIconModule, MatMenuModule],
  templateUrl: './org-switcher.component.html',
  styleUrl: './org-switcher.component.scss',
})
export class OrgSwitcherComponent {
  protected readonly organizationService = inject(OrganizationService);

  select(organizationId: string): void {
    this.organizationService.setActiveOrganization(organizationId);
    // A full reload guarantees every view re-fetches scoped to the newly
    // selected organization rather than requiring each feature to listen
    // for organization changes individually.
    window.location.reload();
  }
}
