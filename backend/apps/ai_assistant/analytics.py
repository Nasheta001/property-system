"""Read-only queries the rule-based assistant answers questions from.

Every function here returns a plain-text summary computed straight from
the organization's own data — the same tables `apps.reports` reads from —
so the assistant's answers are always grounded in what's actually true,
never invented.
"""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment
from apps.properties.models import Unit


def overdue_rent_summary(organization):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    active_leases = Lease.objects.filter(organization=organization, status=Lease.Status.ACTIVE).select_related(
        "unit", "tenant"
    )
    paid_lease_ids = set(
        Payment.objects.filter(
            organization=organization,
            status__in=[Payment.Status.PAID, Payment.Status.SETTLED],
            payment_date__gte=month_start,
        ).values_list("lease_id", flat=True)
    )
    unpaid = [lease for lease in active_leases if lease.id not in paid_lease_ids and lease.billing_day <= today.day]

    if not unpaid:
        return f"No active leases are overdue for {today.strftime('%B')} — every lease due so far this month has a recorded payment."

    lines = [f"{len(unpaid)} lease(s) look overdue for {today.strftime('%B')}:"]
    for lease in unpaid[:10]:
        lines.append(f"- {lease.tenant.full_name} · unit {lease.unit.unit_number} · {lease.rent_amount}")
    if len(unpaid) > 10:
        lines.append(f"...and {len(unpaid) - 10} more.")
    return "\n".join(lines)


def vacancy_summary(organization):
    units = Unit.objects.filter(organization=organization)
    total = units.count()
    if total == 0:
        return "This organization doesn't have any units yet."
    occupied = units.filter(status=Unit.Status.OCCUPIED).count()
    vacant = total - occupied
    rate = round(occupied / total * 100, 1)
    return f"{occupied} of {total} units are occupied ({rate}% occupancy). {vacant} unit(s) are currently vacant."


def maintenance_summary(organization):
    open_statuses = [
        MaintenanceRequest.Status.REPORTED,
        MaintenanceRequest.Status.VERIFIED,
        MaintenanceRequest.Status.ASSIGNED,
        MaintenanceRequest.Status.ACCEPTED,
        MaintenanceRequest.Status.IN_PROGRESS,
        MaintenanceRequest.Status.WAITING_PARTS,
    ]
    open_requests = MaintenanceRequest.objects.filter(organization=organization, status__in=open_statuses)
    count = open_requests.count()
    if count == 0:
        return "There are no open maintenance requests right now."

    urgent = open_requests.filter(priority=MaintenanceRequest.Priority.URGENT).count()
    high = open_requests.filter(priority=MaintenanceRequest.Priority.HIGH).count()
    summary = f"{count} maintenance request(s) are still open."
    if urgent or high:
        summary += f" Of those, {urgent} are urgent and {high} are high priority."
    return summary


def lease_expiration_summary(organization):
    today = timezone.localdate()
    horizon = today + timedelta(days=60)

    expiring = (
        Lease.objects.filter(
            organization=organization,
            status=Lease.Status.ACTIVE,
            end_date__isnull=False,
            end_date__gte=today,
            end_date__lte=horizon,
        )
        .select_related("unit", "tenant")
        .order_by("end_date")
    )
    if not expiring.exists():
        return "No active leases are ending in the next 60 days."

    lines = [f"{expiring.count()} lease(s) end within 60 days:"]
    for lease in expiring[:10]:
        days_left = (lease.end_date - today).days
        lines.append(f"- {lease.tenant.full_name} · unit {lease.unit.unit_number} · in {days_left} day(s)")
    return "\n".join(lines)


def revenue_summary(organization):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    total = (
        Payment.objects.filter(
            organization=organization,
            status__in=[Payment.Status.PAID, Payment.Status.SETTLED],
            payment_date__gte=month_start,
            payment_date__lte=today,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    return f"{total} has been collected in rent so far this month ({month_start.strftime('%B %Y')})."


def organization_snapshot(organization):
    units = Unit.objects.filter(organization=organization)
    active_leases = Lease.objects.filter(organization=organization, status=Lease.Status.ACTIVE).count()
    open_maintenance = MaintenanceRequest.objects.filter(organization=organization).exclude(
        status__in=[MaintenanceRequest.Status.CLOSED, MaintenanceRequest.Status.REVIEWED]
    ).count()
    return (
        f"Organization: {organization.name}\n"
        f"Units: {units.count()} ({units.filter(status=Unit.Status.OCCUPIED).count()} occupied)\n"
        f"Active leases: {active_leases}\n"
        f"Open maintenance requests: {open_maintenance}\n"
        f"Subscription plan: {organization.subscription_plan}"
    )
