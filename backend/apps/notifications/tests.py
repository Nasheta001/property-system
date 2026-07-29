import pytest

from apps.leases.models import Lease
from apps.leases.services import activate_lease, terminate_lease
from apps.notifications.models import Notification
from apps.organizations.models import Membership
from apps.payments.models import Payment
from apps.payments.services import mark_payment_paid

pytestmark = pytest.mark.django_db


@pytest.fixture
def tenant_with_portal_access(tenant_profile, make_user, make_membership):
    portal_user = make_user(email="portal-tenant@example.com")
    make_membership(portal_user, Membership.Role.TENANT)
    tenant_profile.user = portal_user
    tenant_profile.save(update_fields=["user"])
    return tenant_profile


def test_activating_lease_notifies_linked_tenant(unit, tenant_with_portal_access, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_with_portal_access,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )

    activate_lease(lease, owner_user)

    notification = Notification.objects.get(recipient=tenant_with_portal_access.user)
    assert notification.notification_type == Notification.NotificationType.LEASE_ACTIVATED
    assert "A101" in notification.body or unit.unit_number in notification.body


def test_terminating_lease_notifies_linked_tenant(unit, tenant_with_portal_access, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_with_portal_access,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)
    Notification.objects.filter(recipient=tenant_with_portal_access.user).delete()

    terminate_lease(lease, owner_user, reason="Moving out")

    notification = Notification.objects.get(recipient=tenant_with_portal_access.user)
    assert notification.notification_type == Notification.NotificationType.LEASE_TERMINATED


def test_no_notification_when_tenant_has_no_portal_access(unit, tenant_profile, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )

    activate_lease(lease, owner_user)

    assert not Notification.objects.exists()


def test_payment_paid_notifies_tenant(unit, tenant_with_portal_access, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_with_portal_access,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)
    Notification.objects.all().delete()

    payment = Payment.objects.create(
        organization=unit.organization,
        lease=lease,
        tenant=tenant_with_portal_access,
        amount=unit.rent_amount,
        method=Payment.Method.MPESA,
        payment_date="2026-02-01",
        created_by=owner_user,
    )
    mark_payment_paid(payment, owner_user)

    notification = Notification.objects.get(recipient=tenant_with_portal_access.user)
    assert notification.notification_type == Notification.NotificationType.PAYMENT_RECEIVED


def test_new_maintenance_request_notifies_landlord_role_members(
    make_client_for, make_membership, make_user, unit, organization
):
    manager = make_user(email="pm@example.com")
    make_membership(manager, Membership.Role.PROPERTY_MANAGER)

    reporter = make_user(email="reporter@example.com")
    make_membership(reporter, Membership.Role.TENANT)
    reporter_client = make_client_for(reporter)

    response = reporter_client.post(
        "/api/v1/maintenance-requests/", {"unit": str(unit.id), "title": "Broken lock", "priority": "high"}
    )
    assert response.status_code == 201

    assert Notification.objects.filter(recipient=manager).exists()
    assert not Notification.objects.filter(recipient=reporter).exists()


def test_user_only_sees_own_notifications(authenticated_client, owner_user, organization, make_user):
    from apps.notifications.services import notify_user

    other_user = make_user(email="someone-else@example.com")
    notify_user(
        owner_user,
        organization=organization,
        notification_type=Notification.NotificationType.GENERIC,
        title="For owner",
    )
    notify_user(
        other_user,
        organization=organization,
        notification_type=Notification.NotificationType.GENERIC,
        title="For someone else",
    )

    response = authenticated_client.get("/api/v1/notifications/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "For owner"


def test_mark_read_and_mark_all_read(authenticated_client, owner_user, organization):
    from apps.notifications.services import notify_user

    notify_user(owner_user, organization=organization, notification_type=Notification.NotificationType.GENERIC, title="One")
    notify_user(owner_user, organization=organization, notification_type=Notification.NotificationType.GENERIC, title="Two")

    response = authenticated_client.get("/api/v1/notifications/unread-count/")
    assert response.data["count"] == 2

    first_id = Notification.objects.filter(recipient=owner_user).first().id
    response = authenticated_client.post(f"/api/v1/notifications/{first_id}/mark_read/")
    assert response.status_code == 200
    assert response.data["is_read"] is True

    response = authenticated_client.post("/api/v1/notifications/mark-all-read/")
    assert response.status_code == 200

    response = authenticated_client.get("/api/v1/notifications/unread-count/")
    assert response.data["count"] == 0
