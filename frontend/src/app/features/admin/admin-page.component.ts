import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';

import { PlatformOrganization, PlatformStats } from '../../core/models/platform.model';
import { PlatformAdminService } from '../../core/services/platform-admin.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { ReasonDialogComponent } from '../../shared/ui/reason-dialog/reason-dialog.component';

@Component({
  selector: 'app-admin-page',
  imports: [DecimalPipe, MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './admin-page.component.html',
  styleUrl: './admin-page.component.scss',
})
export class AdminPageComponent implements OnInit {
  private readonly platformAdminService = inject(PlatformAdminService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly stats = signal<PlatformStats | null>(null);
  protected readonly organizations = signal<PlatformOrganization[]>([]);

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.isLoading.set(true);
    forkJoin({
      stats: this.platformAdminService.getStats(),
      organizations: this.platformAdminService.listOrganizations(),
    }).subscribe({
      next: ({ stats, organizations }) => {
        this.stats.set(stats);
        this.organizations.set(organizations.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  suspend(organization: PlatformOrganization): void {
    this.dialog
      .open(ReasonDialogComponent, {
        data: {
          title: `Suspend ${organization.name}`,
          message: 'This organization will immediately lose access to the platform.',
          label: 'Reason',
          submitLabel: 'Suspend organization',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((reason) => {
        if (!reason) return;
        this.platformAdminService.suspend(organization.id, reason).subscribe({
          next: () => {
            this.snackBar.open(`${organization.name} suspended.`, 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  reactivate(organization: PlatformOrganization): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: `Reactivate ${organization.name}`,
          message: 'Restore this organization\'s access to the platform?',
          confirmLabel: 'Reactivate',
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.platformAdminService.reactivate(organization.id).subscribe({
          next: () => {
            this.snackBar.open(`${organization.name} reactivated.`, 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
