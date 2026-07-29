import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { Vendor, VendorPayload } from '../../core/models/maintenance.model';

@Component({
  selector: 'app-vendor-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule],
  templateUrl: './vendor-form-dialog.component.html',
  styleUrl: './vendor-form-dialog.component.scss',
})
export class VendorFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<VendorFormDialogComponent, Partial<VendorPayload>>);
  protected readonly vendor = inject<Vendor | null>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    name: [this.vendor?.name ?? '', [Validators.required]],
    contact_person: [this.vendor?.contact_person ?? ''],
    phone_number: [this.vendor?.phone_number ?? ''],
    email: [this.vendor?.email ?? '', [Validators.email]],
    specialty: [this.vendor?.specialty ?? ''],
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
