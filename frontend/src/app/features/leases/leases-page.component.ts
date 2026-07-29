import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Lease, LeaseStatus } from '../../core/models/lease.model';
import { LeasesService } from '../../core/services/leases.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { LeaseFormDialogComponent } from './lease-form-dialog.component';
import { LeaseTerminateDialogComponent } from './lease-terminate-dialog.component';

interface StatusOption {
  value: LeaseStatus | '';
  label: string;
}

@Component({
  selector: 'app-leases-page',
  imports: [
    DecimalPipe,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './leases-page.component.html',
  styleUrl: './leases-page.component.scss',
})
export class LeasesPageComponent implements OnInit {
  private readonly leasesService = inject(LeasesService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly leases = signal<Lease[]>([]);
  protected readonly statusControl = new FormControl<LeaseStatus | ''>('', { nonNullable: true });

  protected readonly statusOptions: StatusOption[] = [
    { value: '', label: 'All statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'active', label: 'Active' },
    { value: 'pending_renewal', label: 'Pending Renewal' },
    { value: 'expired', label: 'Expired' },
    { value: 'terminated', label: 'Terminated' },
  ];

  ngOnInit(): void {
    this.load();
    this.statusControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const status = this.statusControl.value;
    this.leasesService.list(status ? { status } : {}).subscribe({
      next: (response) => {
        this.leases.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateDialog(): void {
    this.dialog
      .open(LeaseFormDialogComponent)
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.leasesService.create(payload).subscribe({
          next: () => {
            this.snackBar.open('Lease created as draft.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  activate(lease: Lease): void {
    this.leasesService.activate(lease.id).subscribe({
      next: () => {
        this.snackBar.open('Lease activated.', 'Dismiss', { duration: 3000 });
        this.load();
      },
      error: (err) => this.showError(err),
    });
  }

  terminate(lease: Lease): void {
    this.dialog
      .open(LeaseTerminateDialogComponent)
      .afterClosed()
      .subscribe((reason) => {
        if (!reason) return;
        this.leasesService.terminate(lease.id, reason).subscribe({
          next: () => {
            this.snackBar.open('Lease terminated.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteLease(lease: Lease): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete lease',
          message: `Delete the ${lease.status} lease for ${lease.tenant_name} on unit ${lease.unit_number}?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.leasesService.delete(lease.id).subscribe({
          next: () => {
            this.snackBar.open('Lease deleted.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  statusTone(status: LeaseStatus): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
    switch (status) {
      case 'active':
        return 'success';
      case 'pending_renewal':
        return 'warning';
      case 'terminated':
      case 'expired':
        return 'danger';
      case 'draft':
      default:
        return 'neutral';
    }
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
