"""Domain services for the payment lifecycle.

Mirrors `apps.leases.services`: transitions that have a financial side
effect (writing a ledger entry, emailing a receipt) live here so every
entry point — API, admin, a future gateway webhook — goes through the same
rules instead of re-implementing them.
"""
from django.db import transaction
from django.utils import timezone

from apps.payments.models import LedgerEntry, Payment


class PaymentTransitionError(Exception):
    """Raised when a requested payment status transition isn't allowed."""


def _generate_receipt_number(payment: Payment) -> str:
    return f"RCPT-{payment.id.hex[:10].upper()}"


def mark_payment_paid(payment: Payment, user, provider_reference: str = "", paid_on=None) -> Payment:
    if payment.status in (Payment.Status.PAID, Payment.Status.SETTLED):
        raise PaymentTransitionError("Payment is already recorded as paid.")
    if payment.status in (Payment.Status.CANCELLED, Payment.Status.REFUNDED):
        raise PaymentTransitionError("A cancelled or refunded payment cannot be marked paid.")

    with transaction.atomic():
        payment.status = Payment.Status.PAID
        payment.provider_reference = provider_reference or payment.provider_reference
        payment.payment_date = paid_on or payment.payment_date or timezone.localdate()
        payment.receipt_number = payment.receipt_number or _generate_receipt_number(payment)
        payment.updated_by = user
        payment.save(
            update_fields=["status", "provider_reference", "payment_date", "receipt_number", "updated_by", "updated_at"]
        )

        LedgerEntry.objects.create(
            organization=payment.organization,
            lease=payment.lease,
            payment=payment,
            entry_type=LedgerEntry.EntryType.PAYMENT,
            amount=payment.amount,
            description=f"Rent payment — {payment.lease.unit.unit_number}",
            created_by=user,
        )

    from apps.payments.tasks import send_receipt_email

    send_receipt_email.delay(str(payment.id))

    return payment


def mark_payment_failed(payment: Payment, user, reason: str = "") -> Payment:
    if payment.status in (Payment.Status.PAID, Payment.Status.SETTLED, Payment.Status.REFUNDED):
        raise PaymentTransitionError("A completed payment cannot be marked as failed.")

    payment.status = Payment.Status.FAILED
    payment.failure_reason = reason
    payment.updated_by = user
    payment.save(update_fields=["status", "failure_reason", "updated_by", "updated_at"])
    return payment


def cancel_payment(payment: Payment, user) -> Payment:
    if payment.status not in (Payment.Status.CREATED, Payment.Status.PENDING, Payment.Status.PROCESSING):
        raise PaymentTransitionError("Only a payment that hasn't completed can be cancelled.")

    payment.status = Payment.Status.CANCELLED
    payment.updated_by = user
    payment.save(update_fields=["status", "updated_by", "updated_at"])
    return payment


def refund_payment(payment: Payment, user, reason: str = "") -> Payment:
    if payment.status not in (Payment.Status.PAID, Payment.Status.SETTLED):
        raise PaymentTransitionError("Only a paid payment can be refunded.")

    with transaction.atomic():
        payment.status = Payment.Status.REFUNDED
        payment.notes = f"{payment.notes}\nRefunded: {reason}".strip() if reason else payment.notes
        payment.updated_by = user
        payment.save(update_fields=["status", "notes", "updated_by", "updated_at"])

        LedgerEntry.objects.create(
            organization=payment.organization,
            lease=payment.lease,
            payment=payment,
            entry_type=LedgerEntry.EntryType.REFUND,
            amount=-payment.amount,
            description=reason or "Payment refunded",
            created_by=user,
        )

    return payment
