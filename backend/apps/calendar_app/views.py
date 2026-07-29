import calendar as stdlib_calendar
from datetime import date, datetime, timedelta

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrganizationMember
from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment

MAX_RANGE_DAYS = 366


def _parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValidationError({field_name: "Expected a date in YYYY-MM-DD format."})


def _months_between(start, end):
    """Yield the first-of-month date for every month touching [start, end]."""
    cursor = start.replace(day=1)
    stop = end.replace(day=1)
    while cursor <= stop:
        yield cursor
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)


class CalendarEventsView(APIView):
    """Aggregates dated events from leases, payments, and maintenance
    requests into a single organization-scoped feed for the calendar UI.

    Rather than a new model, this reads directly off the existing
    domain tables — a calendar is a projection over data that already
    has an owner (leases, payments, maintenance), not a source of truth
    itself.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        today = date.today()
        start = _parse_date(request.query_params.get("start"), "start") if request.query_params.get("start") else today.replace(day=1)
        end = _parse_date(request.query_params.get("end"), "end") if request.query_params.get("end") else start + timedelta(days=31)

        if end < start:
            raise ValidationError({"end": "end must not be before start."})
        if (end - start).days > MAX_RANGE_DAYS:
            raise ValidationError({"end": f"Range cannot exceed {MAX_RANGE_DAYS} days."})

        organization = request.organization
        events = []

        leases = Lease.objects.filter(organization=organization).select_related("unit", "tenant")
        for lease in leases:
            if start <= lease.start_date <= end:
                events.append(
                    {
                        "id": f"lease-start-{lease.id}",
                        "date": lease.start_date.isoformat(),
                        "type": "lease_start",
                        "title": f"Lease starts — {lease.unit.unit_number}",
                        "subtitle": lease.tenant.full_name,
                        "object_type": "lease",
                        "object_id": str(lease.id),
                    }
                )
            if lease.end_date and start <= lease.end_date <= end:
                events.append(
                    {
                        "id": f"lease-end-{lease.id}",
                        "date": lease.end_date.isoformat(),
                        "type": "lease_end",
                        "title": f"Lease ends — {lease.unit.unit_number}",
                        "subtitle": lease.tenant.full_name,
                        "object_type": "lease",
                        "object_id": str(lease.id),
                    }
                )
            if lease.status in (Lease.Status.ACTIVE, Lease.Status.PENDING_RENEWAL):
                for month_start in _months_between(start, end):
                    days_in_month = stdlib_calendar.monthrange(month_start.year, month_start.month)[1]
                    due_date = month_start.replace(day=min(lease.billing_day, days_in_month))
                    if due_date < lease.start_date:
                        continue
                    if lease.end_date and due_date > lease.end_date:
                        continue
                    if not (start <= due_date <= end):
                        continue
                    events.append(
                        {
                            "id": f"rent-due-{lease.id}-{due_date.isoformat()}",
                            "date": due_date.isoformat(),
                            "type": "rent_due",
                            "title": f"Rent due — {lease.unit.unit_number}",
                            "subtitle": f"{lease.tenant.full_name} · {lease.rent_amount}",
                            "object_type": "lease",
                            "object_id": str(lease.id),
                        }
                    )

        payments = Payment.objects.filter(
            organization=organization,
            status__in=[Payment.Status.PAID, Payment.Status.SETTLED],
            payment_date__gte=start,
            payment_date__lte=end,
        ).select_related("tenant")
        for payment in payments:
            events.append(
                {
                    "id": f"payment-{payment.id}",
                    "date": payment.payment_date.isoformat(),
                    "type": "payment_received",
                    "title": f"Payment received — {payment.amount}",
                    "subtitle": payment.tenant.full_name,
                    "object_type": "payment",
                    "object_id": str(payment.id),
                }
            )

        maintenance_requests = MaintenanceRequest.objects.filter(organization=organization).select_related("unit")
        for req in maintenance_requests:
            reported_date = req.created_at.date()
            if start <= reported_date <= end:
                events.append(
                    {
                        "id": f"maintenance-reported-{req.id}",
                        "date": reported_date.isoformat(),
                        "type": "maintenance_reported",
                        "title": f"Maintenance reported — {req.title}",
                        "subtitle": req.unit.unit_number,
                        "object_type": "maintenance",
                        "object_id": str(req.id),
                    }
                )
            if req.completed_at and start <= req.completed_at.date() <= end:
                events.append(
                    {
                        "id": f"maintenance-completed-{req.id}",
                        "date": req.completed_at.date().isoformat(),
                        "type": "maintenance_completed",
                        "title": f"Maintenance completed — {req.title}",
                        "subtitle": req.unit.unit_number,
                        "object_type": "maintenance",
                        "object_id": str(req.id),
                    }
                )

        events.sort(key=lambda event: event["date"])
        return Response({"start": start.isoformat(), "end": end.isoformat(), "events": events})
