import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { SupportTicketPayload } from '../../core/models/support.model';

@Component({
  selector: 'app-ticket-form-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  templateUrl: './ticket-form-dialog.component.html',
  styleUrl: './ticket-form-dialog.component.scss',
})
export class TicketFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<TicketFormDialogComponent, SupportTicketPayload>);

  protected readonly form = this.fb.nonNullable.group({
    subject: ['', [Validators.required]],
    description: ['', [Validators.required]],
    category: ['other', [Validators.required]],
    priority: ['medium', [Validators.required]],
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
