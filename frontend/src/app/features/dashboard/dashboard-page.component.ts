import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { forkJoin } from 'rxjs';

import { OrganizationService } from '../../core/services/organization.service';
import { PropertiesService } from '../../core/services/properties.service';
import { Property } from '../../core/models/property.model';
import { StatCardComponent } from '../../shared/ui/stat-card/stat-card.component';

@Component({
  selector: 'app-dashboard-page',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    StatCardComponent,
  ],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss',
})
export class DashboardPageComponent implements OnInit {
  private readonly propertiesService = inject(PropertiesService);
  private readonly fb = inject(FormBuilder);
  protected readonly organizationService = inject(OrganizationService);

  protected readonly isLoading = signal(true);
  protected readonly propertiesCount = signal(0);
  protected readonly totalUnitsCount = signal(0);
  protected readonly vacantUnitsCount = signal(0);
  protected readonly occupiedUnitsCount = signal(0);
  protected readonly recentProperties = signal<Property[]>([]);

  protected readonly isCreatingOrg = signal(false);
  protected readonly createOrgError = signal<string | null>(null);
  protected readonly createOrgForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    city: [''],
    country: [''],
  });

  ngOnInit(): void {
    if (this.organizationService.activeOrganization()) {
      this.loadDashboardData();
    } else {
      this.isLoading.set(false);
    }
  }

  private loadDashboardData(): void {
    this.isLoading.set(true);
    forkJoin({
      properties: this.propertiesService.list({ page_size: 5, ordering: '-created_at' }),
      units: this.propertiesService.listUnits({ page_size: 1 }),
      vacant: this.propertiesService.listUnits({ page_size: 1, status: 'vacant' }),
      occupied: this.propertiesService.listUnits({ page_size: 1, status: 'occupied' }),
    }).subscribe({
      next: ({ properties, units, vacant, occupied }) => {
        this.propertiesCount.set(properties.count);
        this.recentProperties.set(properties.results);
        this.totalUnitsCount.set(units.count);
        this.vacantUnitsCount.set(vacant.count);
        this.occupiedUnitsCount.set(occupied.count);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  createOrganization(): void {
    if (this.createOrgForm.invalid) {
      this.createOrgForm.markAllAsTouched();
      return;
    }

    this.isCreatingOrg.set(true);
    this.createOrgError.set(null);

    this.organizationService.createOrganization(this.createOrgForm.getRawValue()).subscribe({
      next: (organization) => {
        this.organizationService.setActiveOrganization(organization.id);
        this.isCreatingOrg.set(false);
        this.loadDashboardData();
      },
      error: (err) => {
        this.isCreatingOrg.set(false);
        this.createOrgError.set(err?.error?.error?.message ?? 'Unable to create organization.');
      },
    });
  }
}
