export interface RevenueReportPoint {
  month: string;
  total: string;
  count: number;
}

export interface OccupancyReportRow {
  property_id: string;
  property_name: string;
  total_units: number;
  occupied_units: number;
  occupancy_rate: number;
}

export interface MaintenanceReportCount {
  status?: string;
  category?: string;
  count: number;
}

export interface MaintenanceReport {
  by_status: MaintenanceReportCount[];
  by_category: MaintenanceReportCount[];
}

export interface LeaseExpirationRow {
  lease_id: string;
  unit_number: string;
  tenant_name: string;
  end_date: string;
  days_remaining: number;
}
