"""Domain services enforcing the maintenance request workflow:

    reported -> verified -> assigned -> accepted -> in_progress
             <-> waiting_parts -> completed -> reviewed -> closed

Every forward step goes through `_transition` so the allowed-from check
lives in exactly one place, the same way `apps.leases.services` and
`apps.payments.services` centralize their own status machines.
"""
from django.utils import timezone

from apps.maintenance.models import MaintenanceRequest


class MaintenanceTransitionError(Exception):
    """Raised when a requested workflow transition isn't allowed."""


def _transition(instance, user, *, allowed_from, to_status, timestamp_field=None, extra_fields=None):
    if instance.status not in allowed_from:
        raise MaintenanceTransitionError(
            f"Cannot move from '{instance.get_status_display()}' to "
            f"'{MaintenanceRequest.Status(to_status).label}'."
        )

    update_fields = ["status", "updated_by", "updated_at"]
    instance.status = to_status
    instance.updated_by = user

    if timestamp_field:
        setattr(instance, timestamp_field, timezone.now())
        update_fields.append(timestamp_field)

    for field, value in (extra_fields or {}).items():
        setattr(instance, field, value)
        update_fields.append(field)

    instance.save(update_fields=update_fields)
    return instance


def verify(instance, user):
    return _transition(
        instance, user, allowed_from=[MaintenanceRequest.Status.REPORTED], to_status=MaintenanceRequest.Status.VERIFIED
    )


def assign(instance, user, vendor):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.VERIFIED],
        to_status=MaintenanceRequest.Status.ASSIGNED,
        timestamp_field="assigned_at",
        extra_fields={"vendor": vendor},
    )


def accept(instance, user):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.ASSIGNED],
        to_status=MaintenanceRequest.Status.ACCEPTED,
        timestamp_field="accepted_at",
    )


def start_progress(instance, user):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.ACCEPTED, MaintenanceRequest.Status.WAITING_PARTS],
        to_status=MaintenanceRequest.Status.IN_PROGRESS,
    )


def wait_for_parts(instance, user):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.IN_PROGRESS],
        to_status=MaintenanceRequest.Status.WAITING_PARTS,
    )


def complete(instance, user):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.IN_PROGRESS],
        to_status=MaintenanceRequest.Status.COMPLETED,
        timestamp_field="completed_at",
    )


def review(instance, user):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.COMPLETED],
        to_status=MaintenanceRequest.Status.REVIEWED,
        timestamp_field="reviewed_at",
    )


def close(instance, user, closure_notes: str = ""):
    return _transition(
        instance,
        user,
        allowed_from=[MaintenanceRequest.Status.REVIEWED],
        to_status=MaintenanceRequest.Status.CLOSED,
        timestamp_field="closed_at",
        extra_fields={"closure_notes": closure_notes} if closure_notes else None,
    )
