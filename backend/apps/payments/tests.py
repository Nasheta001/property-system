import pytest

from apps.organizations.models import Membership
from apps.payments.models import LedgerEntry, Payment
from apps.payments.services import (
    PaymentTransitionError,
    cancel_payment,
    mark_payment_failed,
    mark_payment_paid,
    refund_payment,
)

pytestmark = pytest.mark.django_db


def _create_payment(active_lease, owner_user, **overrides):
    defaults = {
        "organization": active_lease.organization,
        "lease": active_lease,
        "tenant": active_lease.tenant,
        "amount": active_lease.rent_amount,
        "method": Payment.Method.MPESA,
        "payment_date": "2026-02-01",
        "created_by": owner_user,
    }
    defaults.update(overrides)
    return Payment.objects.create(**defaults)


def test_create_payment_via_api_defaults_to_created(authenticated_client, active_lease):
    payload = {
        "lease": str(active_lease.id),
        "amount": "25000.00",
        "method": "mpesa",
        "payment_date": "2026-02-01",
    }

    response = authenticated_client.post("/api/v1/payments/", payload)

    assert response.status_code == 201, response.data
    assert response.data["status"] == Payment.Status.CREATED
    assert response.data["tenant_name"] == active_lease.tenant.full_name
    payment = Payment.objects.get(pk=response.data["id"])
    assert payment.tenant_id == active_lease.tenant_id


def test_mark_paid_creates_ledger_entry_and_receipt_number(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)

    paid = mark_payment_paid(payment, owner_user, provider_reference="MPESA123")

    assert paid.status == Payment.Status.PAID
    assert paid.receipt_number.startswith("RCPT-")
    assert paid.provider_reference == "MPESA123"

    entry = LedgerEntry.objects.get(payment=paid)
    assert entry.entry_type == LedgerEntry.EntryType.PAYMENT
    assert entry.amount == paid.amount


def test_cannot_mark_paid_twice(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    mark_payment_paid(payment, owner_user)

    with pytest.raises(PaymentTransitionError):
        mark_payment_paid(payment, owner_user)


def test_refund_creates_negative_ledger_entry(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    mark_payment_paid(payment, owner_user)

    refunded = refund_payment(payment, owner_user, reason="Overpayment")

    assert refunded.status == Payment.Status.REFUNDED
    refund_entry = LedgerEntry.objects.get(payment=refunded, entry_type=LedgerEntry.EntryType.REFUND)
    assert refund_entry.amount == -refunded.amount


def test_cannot_refund_a_payment_that_was_never_paid(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)

    with pytest.raises(PaymentTransitionError):
        refund_payment(payment, owner_user)


def test_cancel_and_fail_transitions(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    cancelled = cancel_payment(payment, owner_user)
    assert cancelled.status == Payment.Status.CANCELLED

    other_payment = _create_payment(active_lease, owner_user)
    failed = mark_payment_failed(other_payment, owner_user, reason="Insufficient funds")
    assert failed.status == Payment.Status.FAILED
    assert failed.failure_reason == "Insufficient funds"


def test_cannot_delete_paid_payment(authenticated_client, active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    mark_payment_paid(payment, owner_user)

    response = authenticated_client.delete(f"/api/v1/payments/{payment.id}/")

    assert response.status_code == 400
    assert Payment.objects.filter(pk=payment.id, deleted_at__isnull=True).exists()


def test_mark_paid_and_refund_via_api(authenticated_client, active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)

    response = authenticated_client.post(f"/api/v1/payments/{payment.id}/mark_paid/", {"provider_reference": "REF1"})
    assert response.status_code == 200
    assert response.data["status"] == Payment.Status.PAID

    response = authenticated_client.post(f"/api/v1/payments/{payment.id}/refund/", {"reason": "Duplicate charge"})
    assert response.status_code == 200
    assert response.data["status"] == Payment.Status.REFUNDED


def test_ledger_entries_are_read_only_via_api(authenticated_client, active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    mark_payment_paid(payment, owner_user)

    response = authenticated_client.get("/api/v1/ledger-entries/")
    assert response.status_code == 200
    assert response.data["count"] == 1

    response = authenticated_client.post("/api/v1/ledger-entries/", {"lease": str(active_lease.id), "amount": "100"})
    assert response.status_code == 405


def test_ledger_entry_model_is_immutable(active_lease, owner_user):
    payment = _create_payment(active_lease, owner_user)
    mark_payment_paid(payment, owner_user)
    entry = LedgerEntry.objects.get(payment=payment)

    entry.description = "tampered"
    with pytest.raises(ValueError):
        entry.save()

    with pytest.raises(ValueError):
        entry.delete()


def test_auditor_can_read_but_not_create_payment(make_client_for, make_membership, make_user, active_lease):
    auditor = make_user(email="auditor@example.com")
    make_membership(auditor, Membership.Role.AUDITOR)
    client = make_client_for(auditor)

    response = client.get("/api/v1/payments/")
    assert response.status_code == 200

    response = client.post(
        "/api/v1/payments/",
        {"lease": str(active_lease.id), "amount": "25000.00", "method": "cash", "payment_date": "2026-02-01"},
    )
    assert response.status_code == 403
