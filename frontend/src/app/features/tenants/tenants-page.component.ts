import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { TenantsService } from '../../core/services/tenants.service';
import { TenantProfile } from '../../core/models/tenant.model';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { TenantFormDialogComponent } from './tenant-form-dialog.component';

@Component({
  selector: 'app-tenants-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './tenants-page.component.html',
  styleUrl: './tenants-page.component.scss',
})
export class TenantsPageComponent implements OnInit {
  private readonly tenantsService = inject(TenantsService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly tenants = signal<TenantProfile[]>([]);
  protected readonly searchControl = new FormControl('', { nonNullable: true });

  ngOnInit(): void {
    this.load();
    this.searchControl.valueChanges.pipe(debounceTime(300), distinctUntilChanged()).subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const search = this.searchControl.value.trim();
    this.tenantsService.list(search ? { search } : {}).subscribe({
      next: (response) => {
        this.tenants.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateDialog(): void {
    this.dialog
      .open(TenantFormDialogComponent, { data: null })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.tenantsService.create(payload).subscribe({
          next: () => {
            this.snackBar.open('Tenant added.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openEditDialog(tenant: TenantProfile): void {
    this.dialog
      .open(TenantFormDialogComponent, { data: tenant })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.tenantsService.update(tenant.id, payload).subscribe({
          next: () => {
            this.snackBar.open('Tenant updated.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteTenant(tenant: TenantProfile): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete tenant',
          message: `Remove ${tenant.full_name} from your tenant list? This can't be undone.`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.tenantsService.delete(tenant.id).subscribe({
          next: () => {
            this.snackBar.open('Tenant deleted.', 'Dismiss', { duration: 3000 });
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
