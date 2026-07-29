import pytest

from apps.activity.models import ActivityLog
from apps.leases.models import Lease
from apps.leases.services import activate_lease
from apps.organizations.models import Membership
from apps.payments.models import Payment
from apps.payments.services import mark_payment_paid
from apps.properties.models import Property

pytestmark = pytest.mark.django_db


def test_creating_property_logs_activity(organization, owner_user):
    Property.objects.create(organization=organization, name="New Property", created_by=owner_user)

    entry = ActivityLog.objects.get(target_type="Property")
    assert "New Property" in entry.verb
    assert entry.actor_name == owner_user.full_name


def test_lease_lifecycle_logs_activity(unit, tenant_profile, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    assert ActivityLog.objects.filter(target_type="Lease", target_id=str(lease.id)).count() == 1

    activate_lease(lease, owner_user)

    entries = ActivityLog.objects.filter(target_type="Lease", target_id=str(lease.id)).order_by("created_at")
    assert entries.count() == 2
    assert "active" in entries.last().verb


def test_payment_paid_logs_activity(unit, tenant_profile, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)

    payment = Payment.objects.create(
        organization=unit.organization,
        lease=lease,
        tenant=tenant_profile,
        amount=unit.rent_amount,
        method=Payment.Method.MPESA,
        payment_date="2026-02-01",
        created_by=owner_user,
    )
    mark_payment_paid(payment, owner_user)

    entries = ActivityLog.objects.filter(target_type="Payment", target_id=str(payment.id))
    assert entries.filter(verb__icontains="recorded").exists()
    assert entries.filter(verb__icontains="paid").exists()


def test_activity_feed_visible_to_all_org_members(make_client_for, make_membership, make_user, organization, owner_user):
    Property.objects.create(organization=organization, name="Visible To All", created_by=owner_user)

    auditor = make_user(email="auditor-feed@example.com")
    make_membership(auditor, Membership.Role.AUDITOR)
    client = make_client_for(auditor)

    response = client.get("/api/v1/activity/")

    assert response.status_code == 200
    assert response.data["count"] >= 1


def test_activity_log_is_read_only_via_api(authenticated_client, organization):
    response = authenticated_client.post("/api/v1/activity/", {"verb": "hand-crafted entry"})
    assert response.status_code == 405


def test_activity_log_model_is_immutable(organization, owner_user):
    Property.objects.create(organization=organization, name="Immutable Test", created_by=owner_user)
    entry = ActivityLog.objects.get(target_type="Property")

    entry.verb = "tampered"
    with pytest.raises(ValueError):
        entry.save()

    with pytest.raises(ValueError):
        entry.delete()
