import pytest

from apps.leases.models import Lease
from apps.leases.services import LeaseTransitionError, activate_lease, expire_due_leases, terminate_lease
from apps.properties.models import Unit

pytestmark = pytest.mark.django_db


def _create_lease(unit, tenant, owner_user, **overrides):
    defaults = {
        "organization": unit.organization,
        "unit": unit,
        "tenant": tenant,
        "start_date": "2026-01-01",
        "rent_amount": unit.rent_amount,
        "deposit_amount": unit.deposit_amount,
        "created_by": owner_user,
    }
    defaults.update(overrides)
    return Lease.objects.create(**defaults)


def test_create_lease_defaults_to_draft(authenticated_client, unit, tenant_profile):
    payload = {
        "unit": str(unit.id),
        "tenant": str(tenant_profile.id),
        "start_date": "2026-02-01",
        "rent_amount": "25000.00",
        "deposit_amount": "25000.00",
        "billing_day": 5,
    }

    response = authenticated_client.post("/api/v1/leases/", payload)

    assert response.status_code == 201, response.data
    assert response.data["status"] == Lease.Status.DRAFT
    unit.refresh_from_db()
    assert unit.status == Unit.Status.VACANT


def test_end_date_must_be_after_start_date(authenticated_client, unit, tenant_profile):
    payload = {
        "unit": str(unit.id),
        "tenant": str(tenant_profile.id),
        "start_date": "2026-02-01",
        "end_date": "2026-01-01",
        "rent_amount": "25000.00",
    }

    response = authenticated_client.post("/api/v1/leases/", payload)

    assert response.status_code == 400
    assert "end_date" in response.data["error"]["details"]


def test_unit_from_another_organization_is_rejected(authenticated_client, tenant_profile, owner_user):
    from apps.organizations.models import Membership, Organization
    from apps.properties.models import Building, Floor, Property

    other_owner = owner_user.__class__.objects.create_user(email="other-owner@example.com", password="TestPassword123!")
    other_org = Organization.objects.create(name="Other Org", owner=other_owner, created_by=other_owner)
    Membership.objects.create(organization=other_org, user=other_owner, role=Membership.Role.OWNER, created_by=other_owner)
    other_property = Property.objects.create(organization=other_org, name="Other Property", created_by=other_owner)
    other_building = Building.objects.create(organization=other_org, property=other_property, name="Block Z", created_by=other_owner)
    other_floor = Floor.objects.create(organization=other_org, building=other_building, number=1, created_by=other_owner)
    other_unit = Unit.objects.create(
        organization=other_org, floor=other_floor, unit_number="Z101", rent_amount=10000, created_by=other_owner
    )

    payload = {
        "unit": str(other_unit.id),
        "tenant": str(tenant_profile.id),
        "start_date": "2026-02-01",
        "rent_amount": "25000.00",
    }

    response = authenticated_client.post("/api/v1/leases/", payload)

    # The unit isn't even a valid choice once scoped to the caller's
    # organization, so DRF rejects it as a bad primary key before our
    # cross-tenant `validate()` check would run.
    assert response.status_code == 400
    assert "unit" in response.data["error"]["details"]


def test_activate_lease_marks_unit_occupied(unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user)

    activated = activate_lease(lease, owner_user)

    assert activated.status == Lease.Status.ACTIVE
    assert activated.signed_at is not None
    unit.refresh_from_db()
    assert unit.status == Unit.Status.OCCUPIED


def test_cannot_activate_when_unit_already_has_active_lease(unit, tenant_profile, owner_user):
    first_lease = _create_lease(unit, tenant_profile, owner_user)
    activate_lease(first_lease, owner_user)

    second_lease = _create_lease(unit, tenant_profile, owner_user, start_date="2026-06-01")

    with pytest.raises(LeaseTransitionError):
        activate_lease(second_lease, owner_user)


def test_terminate_lease_marks_unit_vacant(unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user)
    activate_lease(lease, owner_user)

    terminated = terminate_lease(lease, owner_user, reason="Tenant relocating")

    assert terminated.status == Lease.Status.TERMINATED
    assert terminated.termination_reason == "Tenant relocating"
    unit.refresh_from_db()
    assert unit.status == Unit.Status.VACANT


def test_cannot_terminate_a_draft_lease(unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user)

    with pytest.raises(LeaseTransitionError):
        terminate_lease(lease, owner_user)


def test_activate_and_terminate_via_api(authenticated_client, unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user)

    response = authenticated_client.post(f"/api/v1/leases/{lease.id}/activate/")
    assert response.status_code == 200
    assert response.data["status"] == Lease.Status.ACTIVE

    response = authenticated_client.post(f"/api/v1/leases/{lease.id}/terminate/", {"reason": "Moved out"})
    assert response.status_code == 200
    assert response.data["status"] == Lease.Status.TERMINATED
    assert response.data["termination_reason"] == "Moved out"


def test_cannot_delete_an_active_lease(authenticated_client, unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user)
    activate_lease(lease, owner_user)

    response = authenticated_client.delete(f"/api/v1/leases/{lease.id}/")

    assert response.status_code == 400
    assert Lease.objects.filter(pk=lease.id, deleted_at__isnull=True).exists()


def test_expire_due_leases_frees_unit(unit, tenant_profile, owner_user):
    lease = _create_lease(unit, tenant_profile, owner_user, end_date="2020-01-01")
    activate_lease(lease, owner_user)

    expired_count = expire_due_leases()

    assert expired_count == 1
    lease.refresh_from_db()
    unit.refresh_from_db()
    assert lease.status == Lease.Status.EXPIRED
    assert unit.status == Unit.Status.VACANT


def test_accountant_role_cannot_activate_lease(make_client_for, make_membership, make_user, unit, tenant_profile, owner_user):
    from apps.organizations.models import Membership

    lease = _create_lease(unit, tenant_profile, owner_user)
    accountant = make_user(email="accountant@example.com")
    make_membership(accountant, Membership.Role.ACCOUNTANT)
    client = make_client_for(accountant)

    response = client.post(f"/api/v1/leases/{lease.id}/activate/")

    assert response.status_code == 403
