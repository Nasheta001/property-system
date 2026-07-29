import pytest

from apps.activity.models import ActivityLog
from apps.organizations.models import Membership, Organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_user(make_user):
    return make_user(email="staff@platform.local", is_staff=True)


@pytest.fixture
def staff_client(make_client_for, staff_user):
    return make_client_for(staff_user)


@pytest.fixture
def other_organization(make_user):
    other_owner = make_user(email="other-owner@example.com")
    org = Organization.objects.create(name="Other Org", owner=other_owner, created_by=other_owner)
    Membership.objects.create(organization=org, user=other_owner, role=Membership.Role.OWNER, created_by=other_owner)
    return org


def test_staff_can_list_all_organizations(staff_client, organization, other_organization):
    response = staff_client.get("/api/v1/platform/organizations/")

    assert response.status_code == 200
    names = {row["name"] for row in response.data["results"]}
    assert {organization.name, other_organization.name}.issubset(names)


def test_non_staff_member_cannot_access_platform_endpoints(authenticated_client):
    response = authenticated_client.get("/api/v1/platform/organizations/")
    assert response.status_code == 403

    response = authenticated_client.get("/api/v1/platform/stats/")
    assert response.status_code == 403


def test_platform_stats_aggregates_correctly(staff_client, organization, other_organization, property_obj, unit):
    response = staff_client.get("/api/v1/platform/stats/")

    assert response.status_code == 200
    assert response.data["total_organizations"] == 2
    assert response.data["active_organizations"] == 2
    assert response.data["suspended_organizations"] == 0
    assert response.data["total_properties"] == 1
    assert response.data["total_units"] == 1
    plan_counts = {row["plan"]: row["count"] for row in response.data["plan_breakdown"]}
    assert plan_counts["trial"] == 2


def test_staff_can_suspend_and_reactivate_organization(staff_client, organization):
    response = staff_client.post(f"/api/v1/platform/organizations/{organization.id}/suspend/", {"reason": "Non-payment"})

    assert response.status_code == 200
    assert response.data["is_active"] is False
    organization.refresh_from_db()
    assert organization.is_active is False
    assert ActivityLog.objects.filter(organization=organization, verb__icontains="suspended").exists()

    response = staff_client.post(f"/api/v1/platform/organizations/{organization.id}/reactivate/")

    assert response.status_code == 200
    assert response.data["is_active"] is True
    organization.refresh_from_db()
    assert organization.is_active is True


def test_cannot_suspend_already_suspended_organization(staff_client, organization):
    staff_client.post(f"/api/v1/platform/organizations/{organization.id}/suspend/")

    response = staff_client.post(f"/api/v1/platform/organizations/{organization.id}/suspend/")

    assert response.status_code == 400


def test_platform_endpoints_require_authentication(api_client):
    response = api_client.get("/api/v1/platform/stats/")
    assert response.status_code in (401, 403)
