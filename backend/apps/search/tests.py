import pytest

from apps.properties.models import Property

pytestmark = pytest.mark.django_db


def test_search_returns_matches_across_types(authenticated_client, organization, tenant_profile, unit, owner_user):
    Property.objects.create(organization=organization, name="Amina Gardens", created_by=owner_user)

    response = authenticated_client.get("/api/v1/search/", {"q": "Amina"})

    assert response.status_code == 200
    labels = {result["label"] for result in response.data["results"]}
    assert "Amina Gardens" in labels
    assert tenant_profile.full_name in labels


def test_search_requires_minimum_query_length(authenticated_client):
    response = authenticated_client.get("/api/v1/search/", {"q": "a"})

    assert response.status_code == 200
    assert response.data["results"] == []


def test_search_is_scoped_to_organization(authenticated_client, organization, owner_user):
    from apps.organizations.models import Membership, Organization

    other_owner = owner_user.__class__.objects.create_user(email="search-other@example.com", password="TestPassword123!")
    other_org = Organization.objects.create(name="Other Search Org", owner=other_owner, created_by=other_owner)
    Membership.objects.create(organization=other_org, user=other_owner, role=Membership.Role.OWNER, created_by=other_owner)
    Property.objects.create(organization=other_org, name="Unique Hidden Property", created_by=other_owner)

    response = authenticated_client.get("/api/v1/search/", {"q": "Unique Hidden"})

    assert response.status_code == 200
    assert response.data["results"] == []


def test_search_requires_organization_membership(api_client, owner_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get("/api/v1/search/", {"q": "test"})

    assert response.status_code == 403
