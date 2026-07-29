import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { forkJoin } from 'rxjs';

import {
  LeaseExpirationRow,
  MaintenanceReportCount,
  OccupancyReportRow,
  RevenueReportPoint,
} from '../../core/models/report.model';
import { ReportsService } from '../../core/services/reports.service';

interface BarDatum {
  label: string;
  value: number;
  displayValue: string;
  heightPercent: number;
}

@Component({
  selector: 'app-reports-page',
  imports: [DatePipe, DecimalPipe, MatProgressSpinnerModule],
  templateUrl: './reports-page.component.html',
  styleUrl: './reports-page.component.scss',
})
export class ReportsPageComponent implements OnInit {
  private readonly reportsService = inject(ReportsService);

  protected readonly isLoading = signal(true);
  protected readonly revenue = signal<RevenueReportPoint[]>([]);
  protected readonly occupancy = signal<OccupancyReportRow[]>([]);
  protected readonly maintenanceByStatus = signal<MaintenanceReportCount[]>([]);
  protected readonly maintenanceByCategory = signal<MaintenanceReportCount[]>([]);
  protected readonly leaseExpirations = signal<LeaseExpirationRow[]>([]);

  protected readonly revenueBars = computed<BarDatum[]>(() => {
    const points = this.revenue();
    const max = Math.max(1, ...points.map((point) => Number(point.total)));
    return points.map((point) => ({
      label: this.formatMonth(point.month),
      value: Number(point.total),
      displayValue: Number(point.total).toLocaleString(),
      heightPercent: Math.max(4, (Number(point.total) / max) * 100),
    }));
  });

  protected readonly totalRevenue = computed(() =>
    this.revenue().reduce((sum, point) => sum + Number(point.total), 0)
  );

  protected readonly maintenanceCategoryBars = computed<BarDatum[]>(() => {
    const rows = this.maintenanceByCategory();
    const max = Math.max(1, ...rows.map((row) => row.count));
    return rows
      .map((row) => ({
        label: (row.category ?? '').replace('_', ' '),
        value: row.count,
        displayValue: String(row.count),
        heightPercent: Math.max(6, (row.count / max) * 100),
      }))
      .sort((a, b) => b.value - a.value);
  });

  ngOnInit(): void {
    forkJoin({
      revenue: this.reportsService.revenue(6),
      occupancy: this.reportsService.occupancy(),
      maintenance: this.reportsService.maintenance(),
      leaseExpirations: this.reportsService.leaseExpirations(),
    }).subscribe({
      next: ({ revenue, occupancy, maintenance, leaseExpirations }) => {
        this.revenue.set(revenue);
        this.occupancy.set(occupancy);
        this.maintenanceByStatus.set(maintenance.by_status);
        this.maintenanceByCategory.set(maintenance.by_category);
        this.leaseExpirations.set(leaseExpirations);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  private formatMonth(month: string): string {
    const [year, monthNumber] = month.split('-').map(Number);
    return new Date(year, monthNumber - 1, 1).toLocaleDateString(undefined, { month: 'short' });
  }
}
