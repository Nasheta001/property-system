from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrganizationMember
from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment
from apps.properties.models import Property, Unit


class RevenueReportView(APIView):
    """Total rent collected per month, for however many trailing months
    the caller asks for (default 6). Only PAID/SETTLED payments count —
    a CREATED or FAILED payment never happened financially.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        try:
            months = max(1, min(24, int(request.query_params.get("months", 6))))
        except ValueError:
            months = 6

        since = timezone.localdate().replace(day=1) - timedelta(days=31 * (months - 1))
        since = since.replace(day=1)

        rows = (
            Payment.objects.filter(
                organization=request.organization,
                status__in=[Payment.Status.PAID, Payment.Status.SETTLED],
                payment_date__gte=since,
            )
            .annotate(month=TruncMonth("payment_date"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        return Response(
            [{"month": row["month"].strftime("%Y-%m"), "total": str(row["total"]), "count": row["count"]} for row in rows]
        )


class OccupancyReportView(APIView):
    """Occupied vs. total units, broken down per property."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        data = []
        for property_obj in Property.objects.filter(organization=organization):
            units = Unit.objects.filter(organization=organization, floor__building__property=property_obj)
            total = units.count()
            occupied = units.filter(status=Unit.Status.OCCUPIED).count()
            data.append(
                {
                    "property_id": str(property_obj.id),
                    "property_name": property_obj.name,
                    "total_units": total,
                    "occupied_units": occupied,
                    "occupancy_rate": round(occupied / total * 100, 1) if total else 0.0,
                }
            )
        return Response(data)


class MaintenanceReportView(APIView):
    """Open-request counts grouped by status and by category."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        by_status = list(
            MaintenanceRequest.objects.filter(organization=organization)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        by_category = list(
            MaintenanceRequest.objects.filter(organization=organization)
            .values("category")
            .annotate(count=Count("id"))
            .order_by("category")
        )
        return Response({"by_status": by_status, "by_category": by_category})


class LeaseExpirationReportView(APIView):
    """Active leases with a fixed end date expiring within the next 90 days."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        today = timezone.localdate()
        horizon = today + timedelta(days=90)

        leases = (
            Lease.objects.filter(
                organization=request.organization,
                status=Lease.Status.ACTIVE,
                end_date__isnull=False,
                end_date__gte=today,
                end_date__lte=horizon,
            )
            .select_related("unit", "tenant")
            .order_by("end_date")
        )

        return Response(
            [
                {
                    "lease_id": str(lease.id),
                    "unit_number": lease.unit.unit_number,
                    "tenant_name": lease.tenant.full_name,
                    "end_date": lease.end_date.isoformat(),
                    "days_remaining": (lease.end_date - today).days,
                }
                for lease in leases
            ]
        )
