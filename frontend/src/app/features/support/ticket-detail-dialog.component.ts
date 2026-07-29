import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { SupportTicket, SupportTicketComment } from '../../core/models/support.model';
import { SupportService } from '../../core/services/support.service';

@Component({
  selector: 'app-ticket-detail-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatProgressSpinnerModule],
  templateUrl: './ticket-detail-dialog.component.html',
  styleUrl: './ticket-detail-dialog.component.scss',
})
export class TicketDetailDialogComponent implements OnInit {
  private readonly supportService = inject(SupportService);
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<TicketDetailDialogComponent, boolean>);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly ticket = signal<SupportTicket>(inject(MAT_DIALOG_DATA));
  protected readonly comments = signal<SupportTicketComment[]>([]);
  protected readonly isLoading = signal(true);
  protected readonly isSubmitting = signal(false);
  protected readonly hasChanges = signal(false);

  protected readonly commentForm = this.fb.nonNullable.group({ body: ['', [Validators.required]] });

  ngOnInit(): void {
    this.supportService.listComments(this.ticket().id).subscribe({
      next: (comments) => {
        this.comments.set(comments);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  addComment(): void {
    if (this.commentForm.invalid) {
      this.commentForm.markAllAsTouched();
      return;
    }
    this.supportService.addComment(this.ticket().id, this.commentForm.getRawValue().body).subscribe({
      next: (comment) => {
        this.comments.update((list) => [...list, comment]);
        this.commentForm.reset({ body: '' });
      },
      error: (err) => this.showError(err),
    });
  }

  toggleStatus(): void {
    this.isSubmitting.set(true);
    const action = this.ticket().status === 'closed' ? this.supportService.reopen(this.ticket().id) : this.supportService.close(this.ticket().id);
    action.subscribe({
      next: (updated) => {
        this.ticket.set(updated);
        this.hasChanges.set(true);
        this.isSubmitting.set(false);
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.showError(err);
      },
    });
  }

  dismiss(): void {
    this.dialogRef.close(this.hasChanges());
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
