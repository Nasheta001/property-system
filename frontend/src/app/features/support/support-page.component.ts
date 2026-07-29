import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import { SupportTicket, TicketStatus } from '../../core/models/support.model';
import { SupportService } from '../../core/services/support.service';
import { TicketDetailDialogComponent } from './ticket-detail-dialog.component';
import { TicketFormDialogComponent } from './ticket-form-dialog.component';

interface StatusOption {
  value: TicketStatus | '';
  label: string;
}

@Component({
  selector: 'app-support-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './support-page.component.html',
  styleUrl: './support-page.component.scss',
})
export class SupportPageComponent implements OnInit {
  private readonly supportService = inject(SupportService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly tickets = signal<SupportTicket[]>([]);
  protected readonly statusControl = new FormControl<TicketStatus | ''>('', { nonNullable: true });

  protected readonly statusOptions: StatusOption[] = [
    { value: '', label: 'All statuses' },
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'waiting_on_customer', label: 'Waiting on You' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' },
  ];

  ngOnInit(): void {
    this.load();
    this.statusControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const params: Record<string, string> = {};
    if (this.statusControl.value) params['status'] = this.statusControl.value;

    this.supportService.list(params).subscribe({
      next: (response) => {
        this.tickets.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateDialog(): void {
    this.dialog
      .open(TicketFormDialogComponent)
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.supportService.create(payload).subscribe({
          next: () => {
            this.snackBar.open('Ticket submitted.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openDetail(ticket: SupportTicket): void {
    this.dialog
      .open(TicketDetailDialogComponent, { data: ticket, width: '560px' })
      .afterClosed()
      .subscribe((changed) => {
        if (changed) this.load();
      });
  }

  statusTone(status: TicketStatus): 'neutral' | 'success' | 'warning' | 'info' {
    if (status === 'closed' || status === 'resolved') return 'success';
    if (status === 'waiting_on_customer') return 'warning';
    if (status === 'open') return 'neutral';
    return 'info';
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
