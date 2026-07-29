import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { Floor, FloorPayload } from '../../core/models/property.model';

export interface FloorFormDialogData {
  buildingId: string;
  floor: Floor | null;
}

@Component({
  selector: 'app-floor-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule],
  templateUrl: './floor-form-dialog.component.html',
  styleUrl: './floor-form-dialog.component.scss',
})
export class FloorFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<FloorFormDialogComponent, FloorPayload>);
  protected readonly data = inject<FloorFormDialogData>(MAT_DIALOG_DATA);

  protected readonly form = this.fb.nonNullable.group({
    number: [this.data.floor?.number ?? 1, [Validators.required]],
    name: [this.data.floor?.name ?? ''],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.dialogRef.close({ ...this.form.getRawValue(), building: this.data.buildingId });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
