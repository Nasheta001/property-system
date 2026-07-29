from django.urls import path

from apps.reports.views import (
    LeaseExpirationReportView,
    MaintenanceReportView,
    OccupancyReportView,
    RevenueReportView,
)

urlpatterns = [
    path("reports/revenue/", RevenueReportView.as_view(), name="report-revenue"),
    path("reports/occupancy/", OccupancyReportView.as_view(), name="report-occupancy"),
    path("reports/maintenance/", MaintenanceReportView.as_view(), name="report-maintenance"),
    path("reports/lease-expirations/", LeaseExpirationReportView.as_view(), name="report-lease-expirations"),
]
