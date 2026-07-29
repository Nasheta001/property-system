import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { forkJoin } from 'rxjs';

import { MaintenanceRequestPayload } from '../../core/models/maintenance.model';
import { Unit } from '../../core/models/property.model';
import { TenantProfile } from '../../core/models/tenant.model';
import { PropertiesService } from '../../core/services/properties.service';
import { TenantsService } from '../../core/services/tenants.service';

@Component({
  selector: 'app-maintenance-form-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './maintenance-form-dialog.component.html',
  styleUrl: './maintenance-form-dialog.component.scss',
})
export class MaintenanceFormDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly propertiesService = inject(PropertiesService);
  private readonly tenantsService = inject(TenantsService);
  private readonly dialogRef = inject(MatDialogRef<MaintenanceFormDialogComponent, MaintenanceRequestPayload>);

  protected readonly isLoadingOptions = signal(true);
  protected readonly units = signal<Unit[]>([]);
  protected readonly tenants = signal<TenantProfile[]>([]);

  protected readonly form = this.fb.nonNullable.group({
    unit: ['', [Validators.required]],
    tenant: [''],
    title: ['', [Validators.required]],
    description: [''],
    category: ['other', [Validators.required]],
    priority: ['medium', [Validators.required]],
  });

  ngOnInit(): void {
    forkJoin({
      units: this.propertiesService.listUnits({ page_size: 100 }),
      tenants: this.tenantsService.list({ page_size: 100 }),
    }).subscribe({
      next: ({ units, tenants }) => {
        this.units.set(units.results);
        this.tenants.set(tenants.results);
        this.isLoadingOptions.set(false);
      },
      error: () => this.isLoadingOptions.set(false),
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.dialogRef.close({ ...value, tenant: value.tenant || null });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
