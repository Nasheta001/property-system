import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import { MaintenancePriority, MaintenanceRequest, MaintenanceStatus } from '../../core/models/maintenance.model';
import { MaintenanceService } from '../../core/services/maintenance.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { MaintenanceDetailDialogComponent } from './maintenance-detail-dialog.component';
import { MaintenanceFormDialogComponent } from './maintenance-form-dialog.component';

interface FilterOption<T> {
  value: T | '';
  label: string;
}

@Component({
  selector: 'app-maintenance-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './maintenance-page.component.html',
  styleUrl: './maintenance-page.component.scss',
})
export class MaintenancePageComponent implements OnInit {
  private readonly maintenanceService = inject(MaintenanceService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly requests = signal<MaintenanceRequest[]>([]);
  protected readonly statusControl = new FormControl<MaintenanceStatus | ''>('', { nonNullable: true });
  protected readonly priorityControl = new FormControl<MaintenancePriority | ''>('', { nonNullable: true });

  protected readonly statusOptions: FilterOption<MaintenanceStatus>[] = [
    { value: '', label: 'All statuses' },
    { value: 'reported', label: 'Reported' },
    { value: 'verified', label: 'Verified' },
    { value: 'assigned', label: 'Assigned' },
    { value: 'accepted', label: 'Accepted' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'waiting_parts', label: 'Waiting Parts' },
    { value: 'completed', label: 'Completed' },
    { value: 'reviewed', label: 'Reviewed' },
    { value: 'closed', label: 'Closed' },
  ];

  protected readonly priorityOptions: FilterOption<MaintenancePriority>[] = [
    { value: '', label: 'All priorities' },
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' },
  ];

  ngOnInit(): void {
    this.load();
    this.statusControl.valueChanges.subscribe(() => this.load());
    this.priorityControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const params: Record<string, string> = {};
    if (this.statusControl.value) params['status'] = this.statusControl.value;
    if (this.priorityControl.value) params['priority'] = this.priorityControl.value;

    this.maintenanceService.listRequests(params).subscribe({
      next: (response) => {
        this.requests.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateDialog(): void {
    this.dialog
      .open(MaintenanceFormDialogComponent)
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.maintenanceService.createRequest(payload).subscribe({
          next: () => {
            this.snackBar.open('Issue reported.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openDetail(request: MaintenanceRequest): void {
    this.dialog
      .open(MaintenanceDetailDialogComponent, { data: request, width: '600px' })
      .afterClosed()
      .subscribe((changed) => {
        if (changed) this.load();
      });
  }

  deleteRequest(request: MaintenanceRequest, event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete maintenance request',
          message: `Delete "${request.title}"?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.maintenanceService.deleteRequest(request.id).subscribe({
          next: () => {
            this.snackBar.open('Request deleted.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  priorityTone(priority: MaintenancePriority): 'neutral' | 'warning' | 'danger' {
    if (priority === 'urgent') return 'danger';
    if (priority === 'high') return 'warning';
    return 'neutral';
  }

  statusTone(status: MaintenanceStatus): 'neutral' | 'success' | 'warning' | 'info' {
    if (status === 'closed' || status === 'reviewed') return 'success';
    if (status === 'waiting_parts') return 'warning';
    if (status === 'reported') return 'neutral';
    return 'info';
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
