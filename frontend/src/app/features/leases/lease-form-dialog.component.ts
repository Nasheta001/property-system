import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { forkJoin } from 'rxjs';

import { LeaseCreatePayload } from '../../core/models/lease.model';
import { Unit } from '../../core/models/property.model';
import { TenantProfile } from '../../core/models/tenant.model';
import { PropertiesService } from '../../core/services/properties.service';
import { TenantsService } from '../../core/services/tenants.service';

@Component({
  selector: 'app-lease-form-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './lease-form-dialog.component.html',
  styleUrl: './lease-form-dialog.component.scss',
})
export class LeaseFormDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly propertiesService = inject(PropertiesService);
  private readonly tenantsService = inject(TenantsService);
  private readonly dialogRef = inject(MatDialogRef<LeaseFormDialogComponent, LeaseCreatePayload>);

  protected readonly isLoadingOptions = signal(true);
  protected readonly vacantUnits = signal<Unit[]>([]);
  protected readonly tenants = signal<TenantProfile[]>([]);

  protected readonly form = this.fb.nonNullable.group({
    unit: ['', [Validators.required]],
    tenant: ['', [Validators.required]],
    start_date: ['', [Validators.required]],
    end_date: [''],
    rent_amount: ['', [Validators.required]],
    deposit_amount: ['', [Validators.required]],
    billing_day: [1, [Validators.required, Validators.min(1), Validators.max(28)]],
    notes: [''],
  });

  ngOnInit(): void {
    forkJoin({
      units: this.propertiesService.listUnits({ status: 'vacant', page_size: 100 }),
      tenants: this.tenantsService.list({ page_size: 100 }),
    }).subscribe({
      next: ({ units, tenants }) => {
        this.vacantUnits.set(units.results);
        this.tenants.set(tenants.results);
        this.isLoadingOptions.set(false);
      },
      error: () => this.isLoadingOptions.set(false),
    });
  }

  onUnitSelected(unitId: string): void {
    const unit = this.vacantUnits().find((candidate) => candidate.id === unitId);
    if (unit) {
      this.form.patchValue({ rent_amount: unit.rent_amount, deposit_amount: unit.deposit_amount });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.dialogRef.close({ ...value, end_date: value.end_date || null });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
