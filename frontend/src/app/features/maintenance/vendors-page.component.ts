import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Vendor } from '../../core/models/maintenance.model';
import { MaintenanceService } from '../../core/services/maintenance.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { VendorFormDialogComponent } from './vendor-form-dialog.component';

@Component({
  selector: 'app-vendors-page',
  imports: [MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './vendors-page.component.html',
  styleUrl: './vendors-page.component.scss',
})
export class VendorsPageComponent implements OnInit {
  private readonly maintenanceService = inject(MaintenanceService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly vendors = signal<Vendor[]>([]);

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.isLoading.set(true);
    this.maintenanceService.listVendors().subscribe({
      next: (response) => {
        this.vendors.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateDialog(): void {
    this.dialog
      .open(VendorFormDialogComponent, { data: null })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.maintenanceService.createVendor(payload).subscribe({
          next: () => {
            this.snackBar.open('Vendor added.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openEditDialog(vendor: Vendor): void {
    this.dialog
      .open(VendorFormDialogComponent, { data: vendor })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.maintenanceService.updateVendor(vendor.id, payload).subscribe({
          next: () => {
            this.snackBar.open('Vendor updated.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteVendor(vendor: Vendor): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete vendor',
          message: `Remove ${vendor.name} from your vendor list?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.maintenanceService.deleteVendor(vendor.id).subscribe({
          next: () => {
            this.snackBar.open('Vendor deleted.', 'Dismiss', { duration: 3000 });
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
