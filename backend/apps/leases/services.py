"""Domain services for lease lifecycle transitions.

Activating or terminating a lease always has a side effect on its unit's
occupancy — those two writes must happen together, atomically, regardless
of which view or task triggers the transition. Keeping that rule here
(rather than in the viewset) means it holds no matter how a transition is
initiated in the future (API, admin action, Celery task, AI assistant...).
"""
from django.db import transaction
from django.utils import timezone

from apps.leases.models import Lease
from apps.properties.models import Unit


class LeaseTransitionError(Exception):
    """Raised when a requested lease status transition isn't allowed."""


def activate_lease(lease: Lease, user) -> Lease:
    if lease.status == Lease.Status.ACTIVE:
        raise LeaseTransitionError("Lease is already active.")
    if lease.status in (Lease.Status.TERMINATED, Lease.Status.EXPIRED):
        raise LeaseTransitionError("A terminated or expired lease cannot be reactivated.")

    conflicting_exists = (
        Lease.objects.filter(unit_id=lease.unit_id, status=Lease.Status.ACTIVE).exclude(pk=lease.pk).exists()
    )
    if conflicting_exists:
        raise LeaseTransitionError("This unit already has an active lease.")

    with transaction.atomic():
        lease.status = Lease.Status.ACTIVE
        lease.signed_at = lease.signed_at or timezone.now()
        lease.updated_by = user
        lease.save(update_fields=["status", "signed_at", "updated_by", "updated_at"])

        Unit.objects.filter(pk=lease.unit_id).update(status=Unit.Status.OCCUPIED, updated_by=user)

    lease.refresh_from_db()
    return lease


def terminate_lease(lease: Lease, user, reason: str = "", terminated_at=None) -> Lease:
    if lease.status not in (Lease.Status.ACTIVE, Lease.Status.PENDING_RENEWAL):
        raise LeaseTransitionError("Only an active lease can be terminated.")

    with transaction.atomic():
        lease.status = Lease.Status.TERMINATED
        lease.termination_reason = reason
        lease.terminated_at = terminated_at or timezone.now()
        lease.updated_by = user
        lease.save(
            update_fields=["status", "termination_reason", "terminated_at", "updated_by", "updated_at"]
        )

        Unit.objects.filter(pk=lease.unit_id).update(status=Unit.Status.VACANT, updated_by=user)

    lease.refresh_from_db()
    return lease


def expire_due_leases() -> int:
    """Marks active leases whose end date has passed as expired and frees
    their units. Intended to run on a daily schedule (see `apps.leases.tasks`).
    Returns the number of leases that were expired.
    """
    today = timezone.localdate()
    due_lease_ids = list(
        Lease.objects.filter(status=Lease.Status.ACTIVE, end_date__isnull=False, end_date__lt=today).values_list(
            "id", "unit_id"
        )
    )

    with transaction.atomic():
        for lease_id, unit_id in due_lease_ids:
            Lease.objects.filter(pk=lease_id).update(status=Lease.Status.EXPIRED)
            Unit.objects.filter(pk=unit_id).update(status=Unit.Status.VACANT)

    return len(due_lease_ids)
