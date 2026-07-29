import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { Router } from '@angular/router';

import { ActivityLogEntry } from '../../core/models/activity.model';
import { ActivityService } from '../../core/services/activity.service';

interface TargetTypeOption {
  value: string;
  label: string;
}

@Component({
  selector: 'app-activity-page',
  imports: [DatePipe, ReactiveFormsModule, MatFormFieldModule, MatIconModule, MatProgressSpinnerModule, MatSelectModule],
  templateUrl: './activity-page.component.html',
  styleUrl: './activity-page.component.scss',
})
export class ActivityPageComponent implements OnInit {
  private readonly activityService = inject(ActivityService);
  private readonly router = inject(Router);

  protected readonly isLoading = signal(true);
  protected readonly entries = signal<ActivityLogEntry[]>([]);
  protected readonly targetTypeControl = new FormControl('', { nonNullable: true });

  protected readonly targetTypeOptions: TargetTypeOption[] = [
    { value: '', label: 'Everything' },
    { value: 'Property', label: 'Properties' },
    { value: 'TenantProfile', label: 'Tenants' },
    { value: 'Lease', label: 'Leases' },
    { value: 'Payment', label: 'Payments' },
    { value: 'MaintenanceRequest', label: 'Maintenance' },
    { value: 'Document', label: 'Documents' },
    { value: 'Membership', label: 'Team' },
  ];

  ngOnInit(): void {
    this.load();
    this.targetTypeControl.valueChanges.subscribe(() => this.load());
  }

  private load(): void {
    this.isLoading.set(true);
    const params: Record<string, string> = { page_size: '50' };
    if (this.targetTypeControl.value) params['target_type'] = this.targetTypeControl.value;

    this.activityService.list(params).subscribe({
      next: (response) => {
        this.entries.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  open(entry: ActivityLogEntry): void {
    if (entry.target_link) {
      this.router.navigateByUrl(entry.target_link);
    }
  }

  iconFor(targetType: string): string {
    switch (targetType) {
      case 'Property':
        return 'apartment';
      case 'TenantProfile':
        return 'person';
      case 'Lease':
        return 'description';
      case 'Payment':
        return 'payments';
      case 'MaintenanceRequest':
        return 'build';
      case 'Document':
        return 'folder';
      case 'Membership':
        return 'group_add';
      default:
        return 'history';
    }
  }
}
