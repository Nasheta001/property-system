from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.organizations.models import Membership, Organization
from apps.properties.models import Building, Floor, Property, Unit
from apps.users.models import User


def _auth_headers_for(user, organization):
    access = str(RefreshToken.for_user(user).access_token)
    return {
        "HTTP_AUTHORIZATION": f"Bearer {access}",
        "HTTP_X_ORGANIZATION_ID": str(organization.id),
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make_user(email="user@example.com", password="TestPassword123!", **kwargs):
        return User.objects.create_user(email=email, password=password, **kwargs)

    return _make_user


@pytest.fixture
def owner_user(make_user):
    return make_user(email="owner@example.com", first_name="Owner", last_name="User")


@pytest.fixture
def organization(db, owner_user):
    org = Organization.objects.create(name="Test Org", owner=owner_user, created_by=owner_user)
    Membership.objects.create(
        organization=org, user=owner_user, role=Membership.Role.OWNER, created_by=owner_user
    )
    return org


@pytest.fixture
def make_membership(organization):
    def _make_membership(user, role):
        return Membership.objects.create(organization=organization, user=user, role=role, created_by=organization.owner)

    return _make_membership


@pytest.fixture
def make_client_for(organization):
    def _make(user):
        client = APIClient()
        client.credentials(**_auth_headers_for(user, organization))
        return client

    return _make


@pytest.fixture
def authenticated_client(make_client_for, owner_user):
    return make_client_for(owner_user)


@pytest.fixture
def property_obj(organization, owner_user):
    return Property.objects.create(organization=organization, name="Test Property", created_by=owner_user)


@pytest.fixture
def building(property_obj, owner_user):
    return Building.objects.create(
        organization=property_obj.organization, property=property_obj, name="Block A", created_by=owner_user
    )


@pytest.fixture
def floor(building, owner_user):
    return Floor.objects.create(
        organization=building.organization, building=building, number=1, created_by=owner_user
    )


@pytest.fixture
def unit(floor, owner_user):
    return Unit.objects.create(
        organization=floor.organization,
        floor=floor,
        unit_number="A101",
        rent_amount=Decimal("25000"),
        deposit_amount=Decimal("25000"),
        created_by=owner_user,
    )


@pytest.fixture
def tenant_profile(organization, owner_user):
    from apps.tenants.models import TenantProfile

    return TenantProfile.objects.create(
        organization=organization,
        first_name="Amina",
        last_name="Hassan",
        phone_number="+254700111222",
        email="amina.hassan@example.com",
        created_by=owner_user,
    )


@pytest.fixture
def vendor(organization, owner_user):
    from apps.maintenance.models import Vendor

    return Vendor.objects.create(
        organization=organization,
        name="FixIt Plumbing",
        phone_number="+254700999888",
        specialty="Plumbing",
        created_by=owner_user,
    )


@pytest.fixture
def active_lease(unit, tenant_profile, owner_user):
    from apps.leases.models import Lease
    from apps.leases.services import activate_lease

    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        deposit_amount=unit.deposit_amount,
        created_by=owner_user,
    )
    return activate_lease(lease, owner_user)
