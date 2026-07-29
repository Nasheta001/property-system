import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import { DocumentType, PropertyDocument } from '../../core/models/document.model';
import { DocumentsService } from '../../core/services/documents.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { DocumentUploadDialogComponent } from './document-upload-dialog.component';

interface TypeOption {
  value: DocumentType | '';
  label: string;
}

@Component({
  selector: 'app-documents-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './documents-page.component.html',
  styleUrl: './documents-page.component.scss',
})
export class DocumentsPageComponent implements OnInit {
  private readonly documentsService = inject(DocumentsService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly documents = signal<PropertyDocument[]>([]);
  protected readonly typeControl = new FormControl<DocumentType | ''>('', { nonNullable: true });

  protected readonly typeOptions: TypeOption[] = [
    { value: '', label: 'All types' },
    { value: 'lease_agreement', label: 'Lease Agreement' },
    { value: 'identification', label: 'Identification' },
    { value: 'proof_of_payment', label: 'Proof of Payment' },
    { value: 'inspection_report', label: 'Inspection Report' },
    { value: 'insurance', label: 'Insurance' },
    { value: 'contract', label: 'Contract' },
    { value: 'other', label: 'Other' },
  ];

  ngOnInit(): void {
    this.load();
    this.typeControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const params: Record<string, string> = {};
    if (this.typeControl.value) params['document_type'] = this.typeControl.value;

    this.documentsService.list(params).subscribe({
      next: (response) => {
        this.documents.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openUploadDialog(): void {
    this.dialog
      .open(DocumentUploadDialogComponent)
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.documentsService.upload(payload).subscribe({
          next: () => {
            this.snackBar.open('Document uploaded.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteDocument(document: PropertyDocument): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: { title: 'Delete document', message: `Delete "${document.title}"?`, confirmLabel: 'Delete', danger: true },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.documentsService.delete(document.id).subscribe({
          next: () => {
            this.snackBar.open('Document deleted.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  linkedTo(document: PropertyDocument): string {
    const parts: string[] = [];
    if (document.property_name) parts.push(document.property_name);
    if (document.unit_number) parts.push(document.unit_number);
    if (document.tenant_name) parts.push(document.tenant_name);
    return parts.length > 0 ? parts.join(' · ') : '—';
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
