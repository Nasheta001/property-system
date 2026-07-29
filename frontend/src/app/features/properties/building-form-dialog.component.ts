import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { Building, BuildingPayload } from '../../core/models/property.model';

export interface BuildingFormDialogData {
  propertyId: string;
  building: Building | null;
}

@Component({
  selector: 'app-building-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule],
  templateUrl: './building-form-dialog.component.html',
  styleUrl: './building-form-dialog.component.scss',
})
export class BuildingFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<BuildingFormDialogComponent, BuildingPayload>);
  protected readonly data = inject<BuildingFormDialogData>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    name: [this.data.building?.name ?? '', [Validators.required]],
    code: [this.data.building?.code ?? ''],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.dialogRef.close({ ...this.form.getRawValue(), property: this.data.propertyId });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
