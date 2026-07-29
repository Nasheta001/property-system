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

import { Payment, PaymentStatus } from '../../core/models/payment.model';
import { PaymentsService } from '../../core/services/payments.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { ReasonDialogComponent } from '../../shared/ui/reason-dialog/reason-dialog.component';
import { PaymentFormDialogComponent } from './payment-form-dialog.component';

interface StatusOption {
  value: PaymentStatus | '';
  label: string;
}

@Component({
  selector: 'app-payments-page',
  imports: [
    DecimalPipe,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './payments-page.component.html',
  styleUrl: './payments-page.component.scss',
})
export class PaymentsPageComponent implements OnInit {
  private readonly paymentsService = inject(PaymentsService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly payments = signal<Payment[]>([]);
  protected readonly statusControl = new FormControl<PaymentStatus | ''>('', { nonNullable: true });

  protected readonly statusOptions: StatusOption[] = [
    { value: '', label: 'All statuses' },
    { value: 'created', label: 'Created' },
    { value: 'pending', label: 'Pending' },
    { value: 'processing', label: 'Processing' },
    { value: 'paid', label: 'Paid' },
    { value: 'settled', label: 'Settled' },
    { value: 'refunded', label: 'Refunded' },
    { value: 'cancelled', label: 'Cancelled' },
    { value: 'failed', label: 'Failed' },
  ];

  ngOnInit(): void {
    this.load();
    this.statusControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const status = this.statusControl.value;
    this.paymentsService.list(status ? { status } : {}).subscribe({
      next: (response) => {
        this.payments.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  canMarkPaid(payment: Payment): boolean {
    return ['created', 'pending', 'processing'].includes(payment.status);
  }

  canCancel(payment: Payment): boolean {
    return ['created', 'pending', 'processing'].includes(payment.status);
  }

  canRefund(payment: Payment): boolean {
    return ['paid', 'settled'].includes(payment.status);
  }

  canDelete(payment: Payment): boolean {
    return !['paid', 'settled', 'refunded'].includes(payment.status);
  }

  openCreateDialog(): void {
    this.dialog
      .open(PaymentFormDialogComponent)
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.paymentsService.create(payload).subscribe({
          next: () => {
            this.snackBar.open('Payment recorded.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  markPaid(payment: Payment): void {
    this.paymentsService.markPaid(payment.id).subscribe({
      next: () => {
        this.snackBar.open('Payment marked as paid. Receipt is on its way.', 'Dismiss', { duration: 3000 });
        this.load();
      },
      error: (err) => this.showError(err),
    });
  }

  markFailed(payment: Payment): void {
    this.dialog
      .open(ReasonDialogComponent, {
        data: {
          title: 'Mark payment as failed',
          label: 'Reason',
          submitLabel: 'Mark failed',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((reason) => {
        if (!reason) return;
        this.paymentsService.markFailed(payment.id, reason).subscribe({
          next: () => {
            this.snackBar.open('Payment marked as failed.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  cancel(payment: Payment): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Cancel payment',
          message: `Cancel this ${payment.amount} payment from ${payment.tenant_name}?`,
          confirmLabel: 'Cancel payment',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.paymentsService.cancel(payment.id).subscribe({
          next: () => {
            this.snackBar.open('Payment cancelled.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  refund(payment: Payment): void {
    this.dialog
      .open(ReasonDialogComponent, {
        data: {
          title: 'Refund payment',
          message: 'This will create a negative ledger entry for the refunded amount.',
          label: 'Reason',
          submitLabel: 'Refund',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((reason) => {
        if (!reason) return;
        this.paymentsService.refund(payment.id, reason).subscribe({
          next: () => {
            this.snackBar.open('Payment refunded.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deletePayment(payment: Payment): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete payment',
          message: `Delete this ${payment.status} payment record from ${payment.tenant_name}?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.paymentsService.delete(payment.id).subscribe({
          next: () => {
            this.snackBar.open('Payment deleted.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  statusTone(status: PaymentStatus): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
    switch (status) {
      case 'paid':
      case 'settled':
        return 'success';
      case 'pending':
      case 'processing':
        return 'warning';
      case 'refunded':
      case 'cancelled':
      case 'failed':
        return 'danger';
      case 'created':
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
