import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';

import { Lease } from '../../core/models/lease.model';
import { PaymentCreatePayload } from '../../core/models/payment.model';
import { LeasesService } from '../../core/services/leases.service';

@Component({
  selector: 'app-payment-form-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './payment-form-dialog.component.html',
  styleUrl: './payment-form-dialog.component.scss',
})
export class PaymentFormDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly leasesService = inject(LeasesService);
  private readonly dialogRef = inject(MatDialogRef<PaymentFormDialogComponent, PaymentCreatePayload>);

  protected readonly isLoadingLeases = signal(true);
  protected readonly activeLeases = signal<Lease[]>([]);

  protected readonly form = this.fb.nonNullable.group({
    lease: ['', [Validators.required]],
    amount: ['', [Validators.required]],
    method: ['mpesa', [Validators.required]],
    payment_date: [new Date().toISOString().slice(0, 10), [Validators.required]],
    notes: [''],
  });

  ngOnInit(): void {
    this.leasesService.list({ status: 'active', page_size: 100 }).subscribe({
      next: (response) => {
        this.activeLeases.set(response.results);
        this.isLoadingLeases.set(false);
      },
      error: () => this.isLoadingLeases.set(false),
    });
  }

  onLeaseSelected(leaseId: string): void {
    const lease = this.activeLeases().find((candidate) => candidate.id === leaseId);
    if (lease) {
      this.form.patchValue({ amount: lease.rent_amount });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.dialogRef.close(this.form.getRawValue());
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
