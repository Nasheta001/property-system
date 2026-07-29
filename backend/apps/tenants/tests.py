import pytest

from apps.organizations.models import Membership
from apps.tenants.models import TenantProfile

pytestmark = pytest.mark.django_db


def test_list_requires_organization_membership(api_client, owner_user, organization):
    from rest_framework_simplejwt.tokens import RefreshToken

    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get("/api/v1/tenants/")

    assert response.status_code == 403


def test_owner_can_create_tenant_profile(authenticated_client, organization):
    payload = {
        "first_name": "Brian",
        "last_name": "Otieno",
        "phone_number": "+254700333444",
        "email": "brian.otieno@example.com",
    }

    response = authenticated_client.post("/api/v1/tenants/", payload)

    assert response.status_code == 201, response.data
    assert response.data["full_name"] == "Brian Otieno"
    tenant = TenantProfile.objects.get(pk=response.data["id"])
    assert tenant.organization_id == organization.id
    assert tenant.created_by_id == organization.owner_id


def test_tenant_role_cannot_create_tenant_profile(make_client_for, make_membership, make_user):
    tenant_user = make_user(email="renter@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.post(
        "/api/v1/tenants/",
        {"first_name": "Brian", "last_name": "Otieno", "phone_number": "+254700333444"},
    )

    assert response.status_code == 403


def test_tenant_role_can_read_tenant_profiles(make_client_for, make_membership, make_user, tenant_profile):
    tenant_user = make_user(email="renter2@example.com")
    make_membership(tenant_user, Membership.Role.TENANT)
    client = make_client_for(tenant_user)

    response = client.get("/api/v1/tenants/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_search_tenants_by_name(authenticated_client, tenant_profile):
    response = authenticated_client.get("/api/v1/tenants/", {"search": "Hassan"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(tenant_profile.id)

    response = authenticated_client.get("/api/v1/tenants/", {"search": "Nobody"})
    assert response.data["count"] == 0


def test_cannot_delete_tenant_with_active_lease(authenticated_client, unit, tenant_profile, owner_user):
    from apps.leases.models import Lease
    from apps.leases.services import activate_lease

    lease = Lease.objects.create(
        organization=tenant_profile.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)

    response = authenticated_client.delete(f"/api/v1/tenants/{tenant_profile.id}/")

    assert response.status_code == 400
    assert TenantProfile.objects.filter(pk=tenant_profile.id, deleted_at__isnull=True).exists()
