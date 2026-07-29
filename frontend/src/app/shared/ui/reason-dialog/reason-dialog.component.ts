import { Component, inject } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

export interface ReasonDialogData {
  title: string;
  message?: string;
  label: string;
  submitLabel?: string;
  danger?: boolean;
}

@Component({
  selector: 'app-reason-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule],
  templateUrl: './reason-dialog.component.html',
  styleUrl: './reason-dialog.component.scss',
})
export class ReasonDialogComponent {
  private readonly dialogRef = inject(MatDialogRef<ReasonDialogComponent, string>);
  protected readonly data = inject<ReasonDialogData>(MAT_DIALOG_DATA);
  protected readonly control = new FormControl('', { nonNullable: true, validators: [Validators.required] });

  submit(): void {
    if (this.control.invalid) {
      this.control.markAsTouched();
      return;
    }
    this.dialogRef.close(this.control.value);
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
