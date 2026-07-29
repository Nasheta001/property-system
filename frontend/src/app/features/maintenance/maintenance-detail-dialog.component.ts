import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';

import {
  MaintenanceAttachment,
  MaintenanceComment,
  MaintenanceRequest,
  Vendor,
} from '../../core/models/maintenance.model';
import { MaintenanceService } from '../../core/services/maintenance.service';

@Component({
  selector: 'app-maintenance-detail-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './maintenance-detail-dialog.component.html',
  styleUrl: './maintenance-detail-dialog.component.scss',
})
export class MaintenanceDetailDialogComponent implements OnInit {
  private readonly maintenanceService = inject(MaintenanceService);
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<MaintenanceDetailDialogComponent, boolean>);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly request = signal<MaintenanceRequest>(inject(MAT_DIALOG_DATA));
  protected readonly comments = signal<MaintenanceComment[]>([]);
  protected readonly attachments = signal<MaintenanceAttachment[]>([]);
  protected readonly vendors = signal<Vendor[]>([]);
  protected readonly isLoading = signal(true);
  protected readonly isSubmitting = signal(false);
  protected readonly hasChanges = signal(false);
  protected selectedFile: File | null = null;

  protected readonly commentForm = this.fb.nonNullable.group({ body: ['', [Validators.required]] });
  protected readonly assignForm = this.fb.nonNullable.group({ vendor: ['', [Validators.required]] });
  protected readonly closeForm = this.fb.nonNullable.group({ closure_notes: ['', [Validators.required]] });
  protected readonly attachmentCaption = this.fb.nonNullable.control('');

  ngOnInit(): void {
    forkJoin({
      comments: this.maintenanceService.listComments(this.request().id),
      attachments: this.maintenanceService.listAttachments(this.request().id),
      vendors: this.maintenanceService.listVendors({ page_size: 100, is_active: 'true' }),
    }).subscribe({
      next: ({ comments, attachments, vendors }) => {
        this.comments.set(comments);
        this.attachments.set(attachments);
        this.vendors.set(vendors.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  private applyUpdate(updated: MaintenanceRequest): void {
    this.request.set(updated);
    this.hasChanges.set(true);
    this.isSubmitting.set(false);
  }

  private runTransition(action: (id: string) => ReturnType<MaintenanceService['verify']>): void {
    this.isSubmitting.set(true);
    action(this.request().id).subscribe({
      next: (updated) => this.applyUpdate(updated),
      error: (err) => {
        this.isSubmitting.set(false);
        this.showError(err);
      },
    });
  }

  verify(): void {
    this.runTransition((id) => this.maintenanceService.verify(id));
  }

  assignVendor(): void {
    if (this.assignForm.invalid) {
      this.assignForm.markAllAsTouched();
      return;
    }
    this.runTransition((id) => this.maintenanceService.assign(id, this.assignForm.getRawValue().vendor));
  }

  accept(): void {
    this.runTransition((id) => this.maintenanceService.accept(id));
  }

  startProgress(): void {
    this.runTransition((id) => this.maintenanceService.startProgress(id));
  }

  waitForParts(): void {
    this.runTransition((id) => this.maintenanceService.waitForParts(id));
  }

  complete(): void {
    this.runTransition((id) => this.maintenanceService.complete(id));
  }

  review(): void {
    this.runTransition((id) => this.maintenanceService.review(id));
  }

  closeRequest(): void {
    if (this.closeForm.invalid) {
      this.closeForm.markAllAsTouched();
      return;
    }
    this.runTransition((id) => this.maintenanceService.close(id, this.closeForm.getRawValue().closure_notes));
  }

  addComment(): void {
    if (this.commentForm.invalid) {
      this.commentForm.markAllAsTouched();
      return;
    }
    this.maintenanceService.addComment(this.request().id, this.commentForm.getRawValue().body).subscribe({
      next: (comment) => {
        this.comments.update((list) => [...list, comment]);
        this.commentForm.reset({ body: '' });
      },
      error: (err) => this.showError(err),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
  }

  uploadAttachment(): void {
    if (!this.selectedFile) return;
    this.maintenanceService.uploadAttachment(this.request().id, this.selectedFile, this.attachmentCaption.value).subscribe({
      next: (attachment) => {
        this.attachments.update((list) => [attachment, ...list]);
        this.selectedFile = null;
        this.attachmentCaption.setValue('');
      },
      error: (err) => this.showError(err),
    });
  }

  close(): void {
    this.dialogRef.close(this.hasChanges());
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
