import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.organizations.models import Organization
from apps.properties.models import Property
from apps.subscriptions.models import SubscriptionEvent

pytestmark = pytest.mark.django_db


def test_plan_catalog_lists_all_plans(authenticated_client):
    response = authenticated_client.get("/api/v1/subscriptions/plans/")

    assert response.status_code == 200
    codes = {plan["code"] for plan in response.data}
    assert codes == {"trial", "starter", "professional", "enterprise"}


def test_current_subscription_returns_plan_and_usage(authenticated_client, organization, property_obj, unit):
    response = authenticated_client.get("/api/v1/subscriptions/current/")

    assert response.status_code == 200
    assert response.data["plan"]["code"] == organization.subscription_plan == "trial"
    assert response.data["usage"]["properties"] == 1
    assert response.data["usage"]["units"] == 1
    assert response.data["usage"]["team_members"] == 1


def test_owner_can_change_plan(authenticated_client, organization, owner_user):
    response = authenticated_client.post("/api/v1/subscriptions/current/", {"plan": "starter", "reason": "Growing"})

    assert response.status_code == 200
    assert response.data["plan"]["code"] == "starter"

    organization.refresh_from_db()
    assert organization.subscription_plan == "starter"

    event = SubscriptionEvent.objects.get(organization=organization)
    assert event.previous_plan == "trial"
    assert event.new_plan == "starter"
    assert event.changed_by_id == owner_user.id
    assert event.reason == "Growing"


def test_non_admin_cannot_change_plan(make_client_for, make_user, make_membership):
    member = make_user(email="pm@example.com")
    make_membership(member, "property_manager")
    client = make_client_for(member)

    response = client.post("/api/v1/subscriptions/current/", {"plan": "starter"})

    assert response.status_code == 403


def test_cannot_switch_to_same_plan(authenticated_client):
    response = authenticated_client.post("/api/v1/subscriptions/current/", {"plan": "trial"})

    assert response.status_code == 400


def test_downgrade_blocked_when_over_limit(authenticated_client, organization, owner_user):
    organization.subscription_plan = Organization.SubscriptionPlan.PROFESSIONAL
    organization.save(update_fields=["subscription_plan"])

    for i in range(4):
        Property.objects.create(organization=organization, name=f"Property {i}", created_by=owner_user)

    response = authenticated_client.post("/api/v1/subscriptions/current/", {"plan": "starter"})

    assert response.status_code == 400
    organization.refresh_from_db()
    assert organization.subscription_plan == Organization.SubscriptionPlan.PROFESSIONAL


def test_events_endpoint_lists_history(authenticated_client):
    authenticated_client.post("/api/v1/subscriptions/current/", {"plan": "starter"})

    response = authenticated_client.get("/api/v1/subscriptions/events/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["previous_plan"] == "trial"
    assert response.data["results"][0]["new_plan"] == "starter"


def test_requires_organization_membership(api_client, owner_user):
    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get("/api/v1/subscriptions/current/")

    assert response.status_code == 403
