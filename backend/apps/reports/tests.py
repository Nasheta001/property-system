from datetime import timedelta

import pytest
from django.utils import timezone

from apps.leases.models import Lease
from apps.leases.services import activate_lease
from apps.maintenance.models import MaintenanceRequest
from apps.payments.models import Payment
from apps.payments.services import mark_payment_paid

pytestmark = pytest.mark.django_db


def test_revenue_report_aggregates_paid_payments_by_month(authenticated_client, unit, tenant_profile, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)

    today = timezone.localdate()
    payment = Payment.objects.create(
        organization=unit.organization,
        lease=lease,
        tenant=tenant_profile,
        amount=unit.rent_amount,
        method=Payment.Method.MPESA,
        payment_date=today,
        created_by=owner_user,
    )
    mark_payment_paid(payment, owner_user)

    # A created-but-never-paid payment must not count towards revenue.
    Payment.objects.create(
        organization=unit.organization,
        lease=lease,
        tenant=tenant_profile,
        amount=unit.rent_amount,
        method=Payment.Method.CASH,
        payment_date=today,
        created_by=owner_user,
    )

    response = authenticated_client.get("/api/v1/reports/revenue/", {"months": 1})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["count"] == 1
    assert float(response.data[0]["total"]) == float(unit.rent_amount)


def test_occupancy_report_calculates_rate_per_property(authenticated_client, unit, tenant_profile, owner_user):
    lease = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date="2026-01-01",
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease, owner_user)

    response = authenticated_client.get("/api/v1/reports/occupancy/")

    assert response.status_code == 200
    row = next(r for r in response.data if r["property_id"] == str(unit.floor.building.property_id))
    assert row["total_units"] == 1
    assert row["occupied_units"] == 1
    assert row["occupancy_rate"] == 100.0


def test_maintenance_report_groups_by_status_and_category(authenticated_client, unit, owner_user):
    MaintenanceRequest.objects.create(
        organization=unit.organization,
        unit=unit,
        title="Leak",
        category=MaintenanceRequest.Category.PLUMBING,
        created_by=owner_user,
    )
    MaintenanceRequest.objects.create(
        organization=unit.organization,
        unit=unit,
        title="Fuse",
        category=MaintenanceRequest.Category.ELECTRICAL,
        created_by=owner_user,
    )

    response = authenticated_client.get("/api/v1/reports/maintenance/")

    assert response.status_code == 200
    status_counts = {row["status"]: row["count"] for row in response.data["by_status"]}
    assert status_counts.get("reported") == 2
    category_counts = {row["category"]: row["count"] for row in response.data["by_category"]}
    assert category_counts.get("plumbing") == 1
    assert category_counts.get("electrical") == 1


def test_lease_expiration_report_lists_only_upcoming(authenticated_client, unit, tenant_profile, owner_user):
    today = timezone.localdate()

    lease_soon = Lease.objects.create(
        organization=unit.organization,
        unit=unit,
        tenant=tenant_profile,
        start_date=today - timedelta(days=300),
        end_date=today + timedelta(days=30),
        rent_amount=unit.rent_amount,
        created_by=owner_user,
    )
    activate_lease(lease_soon, owner_user)

    response = authenticated_client.get("/api/v1/reports/lease-expirations/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["lease_id"] == str(lease_soon.id)
    assert response.data[0]["days_remaining"] == 30


def test_reports_require_organization_membership(api_client, owner_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    access = str(RefreshToken.for_user(owner_user).access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get("/api/v1/reports/revenue/")

    assert response.status_code == 403
