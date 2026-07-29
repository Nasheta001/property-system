from datetime import date

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment
from apps.payments.services import mark_payment_paid

pytestmark = pytest.mark.django_db


def test_calendar_includes_lease_start_and_rent_due(authenticated_client, active_lease):
    response = authenticated_client.get(
        "/api/v1/calendar/events/", {"start": "2026-01-01", "end": "2026-01-31"}
    )

    assert response.status_code == 200
    types = {event["type"] for event in response.data["events"]}
    assert "lease_start" in types
    assert "rent_due" in types

    rent_due_dates = [event["date"] for event in response.data["events"] if event["type"] == "rent_due"]
    assert rent_due_dates == ["2026-01-01"]


def test_calendar_rent_due_stops_after_lease_end_date(authenticated_client, active_lease):
    active_lease.end_date = date(2026, 2, 15)
    active_lease.save(update_fields=["end_date"])

    response = authenticated_client.get(
        "/api/v1/calendar/events/", {"start": "2026-03-01", "end": "2026-03-31"}
    )

    assert response.status_code == 200
    rent_due = [event for event in response.data["events"] if event["type"] == "rent_due"]
    assert rent_due == []


def test_calendar_includes_received_payment(authenticated_client, active_lease, owner_user):
    payment = Payment.objects.create(
        organization=active_lease.organization,
        lease=active_lease,
        tenant=active_lease.tenant,
        amount=active_lease.rent_amount,
        method=Payment.Method.MPESA,
        payment_date=date(2026, 1, 5),
        created_by=owner_user,
    )
    mark_payment_paid(payment, owner_user)

    response = authenticated_client.get(
        "/api/v1/calendar/events/", {"start": "2026-01-01", "end": "2026-01-31"}
    )

    payment_events = [event for event in response.data["events"] if event["type"] == "payment_received"]
    assert len(payment_events) == 1
    assert payment_events[0]["date"] == "2026-01-05"
    assert payment_events[0]["object_id"] == str(payment.id)


def test_calendar_includes_maintenance_reported(authenticated_client, unit, owner_user):
    request = MaintenanceRequest.objects.create(
        organization=unit.organization,
        unit=unit,
        title="Leaking tap",
        created_by=owner_user,
    )
    today = request.created_at.date()

    response = authenticated_client.get(
        "/api/v1/calendar/events/", {"start": today.isoformat(), "end": today.isoformat()}
    )

    reported = [event for event in response.data["events"] if event["type"] == "maintenance_reported"]
    assert len(reported) == 1
    assert reported[0]["object_id"] == str(request.id)


def test_calendar_defaults_to_current_month_without_params(authenticated_client, active_lease):
    response = authenticated_client.get("/api/v1/calendar/events/")

    assert response.status_code == 200
    assert "start" in response.data
    assert "end" in response.data


def test_calendar_rejects_end_before_start(authenticated_client):
    response = authenticated_client.get(
        "/api/v1/calendar/events/", {"start": "2026-02-01", "end": "2026-01-01"}
    )

    assert response.status_code == 400


def test_calendar_requires_organization_membership(api_client, owner_user):
    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get("/api/v1/calendar/events/")

    assert response.status_code == 403
