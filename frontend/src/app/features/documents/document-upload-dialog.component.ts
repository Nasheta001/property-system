import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { forkJoin } from 'rxjs';

import { DocumentUploadPayload } from '../../core/services/documents.service';
import { Lease } from '../../core/models/lease.model';
import { Property } from '../../core/models/property.model';
import { TenantProfile } from '../../core/models/tenant.model';
import { LeasesService } from '../../core/services/leases.service';
import { PropertiesService } from '../../core/services/properties.service';
import { TenantsService } from '../../core/services/tenants.service';

@Component({
  selector: 'app-document-upload-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './document-upload-dialog.component.html',
  styleUrl: './document-upload-dialog.component.scss',
})
export class DocumentUploadDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly propertiesService = inject(PropertiesService);
  private readonly leasesService = inject(LeasesService);
  private readonly tenantsService = inject(TenantsService);
  private readonly dialogRef = inject(MatDialogRef<DocumentUploadDialogComponent, DocumentUploadPayload>);

  protected readonly isLoadingOptions = signal(true);
  protected readonly properties = signal<Property[]>([]);
  protected readonly leases = signal<Lease[]>([]);
  protected readonly tenants = signal<TenantProfile[]>([]);
  protected selectedFile: File | null = null;
  protected fileError = '';

  protected readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required]],
    document_type: ['other', [Validators.required]],
    description: [''],
    property: [''],
    lease: [''],
    tenant: [''],
  });

  ngOnInit(): void {
    forkJoin({
      properties: this.propertiesService.list({ page_size: 100 }),
      leases: this.leasesService.list({ page_size: 100 }),
      tenants: this.tenantsService.list({ page_size: 100 }),
    }).subscribe({
      next: ({ properties, leases, tenants }) => {
        this.properties.set(properties.results);
        this.leases.set(leases.results);
        this.tenants.set(tenants.results);
        this.isLoadingOptions.set(false);
      },
      error: () => this.isLoadingOptions.set(false),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
    this.fileError = '';
  }

  submit(): void {
    if (this.form.invalid || !this.selectedFile) {
      this.form.markAllAsTouched();
      if (!this.selectedFile) this.fileError = 'Select a file to upload.';
      return;
    }
    const value = this.form.getRawValue();
    this.dialogRef.close({
      title: value.title,
      document_type: value.document_type as DocumentUploadPayload['document_type'],
      description: value.description,
      property: value.property || undefined,
      lease: value.lease || undefined,
      tenant: value.tenant || undefined,
      file: this.selectedFile,
    });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
