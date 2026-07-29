import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { Property, PropertyPayload } from '../../core/models/property.model';

@Component({
  selector: 'app-property-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  templateUrl: './property-form-dialog.component.html',
  styleUrl: './property-form-dialog.component.scss',
})
export class PropertyFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<PropertyFormDialogComponent, Partial<PropertyPayload>>);
  protected readonly property = inject<Property | null>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    name: [this.property?.name ?? '', [Validators.required]],
    property_type: [this.property?.property_type ?? 'residential', [Validators.required]],
    description: [this.property?.description ?? ''],
    address: [this.property?.address ?? ''],
    city: [this.property?.city ?? ''],
    country: [this.property?.country ?? ''],
    is_active: [this.property?.is_active ?? true],
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
