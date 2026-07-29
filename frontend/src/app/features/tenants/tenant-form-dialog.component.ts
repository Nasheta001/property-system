import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { TenantProfile, TenantProfilePayload } from '../../core/models/tenant.model';

@Component({
  selector: 'app-tenant-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule],
  templateUrl: './tenant-form-dialog.component.html',
  styleUrl: './tenant-form-dialog.component.scss',
})
export class TenantFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<TenantFormDialogComponent, Partial<TenantProfilePayload>>);
  protected readonly tenant = inject<TenantProfile | null>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    first_name: [this.tenant?.first_name ?? '', [Validators.required]],
    last_name: [this.tenant?.last_name ?? '', [Validators.required]],
    phone_number: [this.tenant?.phone_number ?? '', [Validators.required]],
    email: [this.tenant?.email ?? '', [Validators.email]],
    national_id: [this.tenant?.national_id ?? ''],
    occupation: [this.tenant?.occupation ?? ''],
    employer: [this.tenant?.employer ?? ''],
    emergency_contact_name: [this.tenant?.emergency_contact_name ?? ''],
    emergency_contact_phone: [this.tenant?.emergency_contact_phone ?? ''],
    notes: [this.tenant?.notes ?? ''],
  });

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
