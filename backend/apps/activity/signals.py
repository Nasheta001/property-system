"""Wires domain events from other apps to the activity feed.

Same decoupled shape as `apps.notifications.signals`: nothing in
organizations/properties/tenants/leases/payments/maintenance/documents
knows this module exists.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.activity.services import log_activity
from apps.documents.models import Document
from apps.leases.models import Lease
from apps.maintenance.models import MaintenanceRequest
from apps.organizations.models import Membership
from apps.payments.models import Payment
from apps.properties.models import Property
from apps.tenants.models import TenantProfile


@receiver(post_save, sender=Membership)
def log_membership_created(sender, instance, created, **kwargs):
    if not created:
        return
    log_activity(
        instance.organization,
        instance.invited_by,
        f"added {instance.user.full_name} as {instance.get_role_display()}",
        target_type="Membership",
        target_id=instance.id,
    )


@receiver(post_save, sender=Property)
def log_property_created(sender, instance, created, **kwargs):
    if not created:
        return
    log_activity(
        instance.organization,
        instance.created_by,
        f'added property "{instance.name}"',
        target_type="Property",
        target_id=instance.id,
        target_link="/properties",
    )


@receiver(post_save, sender=TenantProfile)
def log_tenant_created(sender, instance, created, **kwargs):
    if not created:
        return
    log_activity(
        instance.organization,
        instance.created_by,
        f"added tenant {instance.full_name}",
        target_type="TenantProfile",
        target_id=instance.id,
        target_link="/tenants",
    )


@receiver(post_save, sender=Lease)
def log_lease_activity(sender, instance, created, update_fields=None, **kwargs):
    if created:
        log_activity(
            instance.organization,
            instance.created_by,
            f"created a lease for unit {instance.unit.unit_number}",
            target_type="Lease",
            target_id=instance.id,
            target_link="/leases",
        )
        return
    if update_fields and "status" in update_fields:
        log_activity(
            instance.organization,
            instance.updated_by,
            f"{instance.get_status_display().lower()} the lease for unit {instance.unit.unit_number}",
            target_type="Lease",
            target_id=instance.id,
            target_link="/leases",
        )


@receiver(post_save, sender=Payment)
def log_payment_activity(sender, instance, created, update_fields=None, **kwargs):
    if created:
        log_activity(
            instance.organization,
            instance.created_by,
            f"recorded a payment of {instance.amount} from {instance.tenant.full_name}",
            target_type="Payment",
            target_id=instance.id,
            target_link="/payments",
        )
        return
    if update_fields and "status" in update_fields and instance.status in (
        Payment.Status.PAID,
        Payment.Status.REFUNDED,
    ):
        log_activity(
            instance.organization,
            instance.updated_by,
            f"marked a payment of {instance.amount} as {instance.status}",
            target_type="Payment",
            target_id=instance.id,
            target_link="/payments",
        )


@receiver(post_save, sender=MaintenanceRequest)
def log_maintenance_activity(sender, instance, created, update_fields=None, **kwargs):
    if created:
        log_activity(
            instance.organization,
            instance.reported_by,
            f'reported "{instance.title}" for unit {instance.unit.unit_number}',
            target_type="MaintenanceRequest",
            target_id=instance.id,
            target_link="/maintenance",
        )
        return
    if update_fields and "status" in update_fields:
        log_activity(
            instance.organization,
            instance.updated_by,
            f'marked "{instance.title}" as {instance.get_status_display().lower()}',
            target_type="MaintenanceRequest",
            target_id=instance.id,
            target_link="/maintenance",
        )


@receiver(post_save, sender=Document)
def log_document_activity(sender, instance, created, **kwargs):
    if not created:
        return
    log_activity(
        instance.organization,
        instance.uploaded_by,
        f'uploaded document "{instance.title}"',
        target_type="Document",
        target_id=instance.id,
        target_link="/documents",
    )
