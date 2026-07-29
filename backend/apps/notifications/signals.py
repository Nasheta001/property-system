"""Wires domain events from other apps to in-app notifications.

Deliberately one-directional and decoupled: apps.leases, apps.payments and
apps.maintenance have no knowledge this module exists. Each handler
inspects `update_fields` to react only to the specific transition it
cares about, since these models are saved with an explicit
`update_fields` list on every status change (see each app's `services.py`).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.notifications.models import Notification
from apps.notifications.services import notify_organization_roles, notify_user
from apps.payments.models import Payment


def _status_changed_to(update_fields, target_status, instance):
    return bool(update_fields) and "status" in update_fields and instance.status == target_status


@receiver(post_save, sender=Lease)
def handle_lease_status_change(sender, instance, created, update_fields=None, **kwargs):
    if created or instance.tenant_id is None or instance.tenant.user_id is None:
        return

    if _status_changed_to(update_fields, Lease.Status.ACTIVE, instance):
        notify_user(
            instance.tenant.user,
            organization=instance.organization,
            notification_type=Notification.NotificationType.LEASE_ACTIVATED,
            title="Your lease is now active",
            body=f"Your lease for unit {instance.unit.unit_number} is now active.",
            link="/leases",
        )
    elif _status_changed_to(update_fields, Lease.Status.TERMINATED, instance):
        notify_user(
            instance.tenant.user,
            organization=instance.organization,
            notification_type=Notification.NotificationType.LEASE_TERMINATED,
            title="Your lease has been terminated",
            body=f"Your lease for unit {instance.unit.unit_number} was terminated.",
            link="/leases",
        )


@receiver(post_save, sender=Payment)
def handle_payment_status_change(sender, instance, created, update_fields=None, **kwargs):
    if created or instance.tenant.user_id is None:
        return

    if _status_changed_to(update_fields, Payment.Status.PAID, instance):
        notify_user(
            instance.tenant.user,
            organization=instance.organization,
            notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
            title="Payment received",
            body=f"We received your payment of {instance.amount} for unit {instance.lease.unit.unit_number}.",
            link="/payments",
        )
    elif _status_changed_to(update_fields, Payment.Status.REFUNDED, instance):
        notify_user(
            instance.tenant.user,
            organization=instance.organization,
            notification_type=Notification.NotificationType.PAYMENT_REFUNDED,
            title="Payment refunded",
            body=f"Your payment of {instance.amount} was refunded.",
            link="/payments",
        )


@receiver(post_save, sender=MaintenanceRequest)
def handle_maintenance_request_change(sender, instance, created, update_fields=None, **kwargs):
    if created:
        notify_organization_roles(
            instance.organization,
            min_role="landlord",
            notification_type=Notification.NotificationType.MAINTENANCE_REPORTED,
            title="New maintenance request",
            body=f'"{instance.title}" was reported for unit {instance.unit.unit_number}.',
            link="/maintenance",
            exclude_user=instance.reported_by,
        )
        return

    if instance.reported_by_id and update_fields and "status" in update_fields:
        notify_user(
            instance.reported_by,
            organization=instance.organization,
            notification_type=Notification.NotificationType.MAINTENANCE_STATUS_CHANGED,
            title=f"Maintenance request {instance.get_status_display().lower()}",
            body=instance.title,
            link="/maintenance",
        )
