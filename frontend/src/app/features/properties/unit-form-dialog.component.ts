import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { Unit, UnitPayload } from '../../core/models/property.model';

export interface UnitFormDialogData {
  floorId: string;
  unit: Unit | null;
}

@Component({
  selector: 'app-unit-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  templateUrl: './unit-form-dialog.component.html',
  styleUrl: './unit-form-dialog.component.scss',
})
export class UnitFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<UnitFormDialogComponent, UnitPayload>);
  protected readonly data = inject<UnitFormDialogData>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    unit_number: [this.data.unit?.unit_number ?? '', [Validators.required]],
    unit_type: [this.data.unit?.unit_type ?? 'one_bedroom', [Validators.required]],
    bedrooms: [this.data.unit?.bedrooms ?? 1, [Validators.required, Validators.min(0)]],
    bathrooms: [this.data.unit?.bathrooms ?? 1, [Validators.required, Validators.min(0)]],
    size_sqm: [this.data.unit?.size_sqm ?? ''],
    rent_amount: [this.data.unit?.rent_amount ?? '', [Validators.required]],
    deposit_amount: [this.data.unit?.deposit_amount ?? '', [Validators.required]],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.dialogRef.close({ ...value, size_sqm: value.size_sqm || null, floor: this.data.floorId });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
