from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import OrganizationScopedModel


class Payment(OrganizationScopedModel):
    """A rent payment against a `Lease`.

    Payments are recorded by a property manager/accountant (either after
    receiving an M-Pesa/bank/card payment, or via a future gateway webhook)
    and move through the lifecycle below. Once a payment reaches `PAID` it
    produces an immutable `LedgerEntry` — the payment row itself may still
    later move to `REFUNDED`, but the financial history it already wrote is
    never edited, only appended to.
    """

    class Method(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CASH = "cash", "Cash"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PAID = "paid", "Paid"
        SETTLED = "settled", "Settled"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    lease = models.ForeignKey("leases.Lease", related_name="payments", on_delete=models.PROTECT)
    tenant = models.ForeignKey("tenants.TenantProfile", related_name="payments", on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, db_index=True)

    provider_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(help_text="Date the payment was received.")
    receipt_number = models.CharField(max_length=32, blank=True)
    receipt_sent_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "lease"]),
        ]

    def __str__(self):
        return f"{self.amount} from {self.tenant} ({self.status})"


class LedgerEntry(OrganizationScopedModel):
    """An append-only financial record. Never updated or deleted once
    written — `save()`/`delete()` enforce that below — so it can always be
    trusted as the source of truth for a lease's payment history.
    """

    class EntryType(models.TextChoices):
        PAYMENT = "payment", "Payment"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"

    lease = models.ForeignKey("leases.Lease", related_name="ledger_entries", on_delete=models.PROTECT)
    payment = models.ForeignKey(
        Payment, related_name="ledger_entries", on_delete=models.PROTECT, null=True, blank=True
    )
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Positive for money received, negative for refunds/adjustments."
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ledger Entry"
        verbose_name_plural = "Ledger Entries"
        indexes = [models.Index(fields=["organization", "lease"])]

    def __str__(self):
        return f"{self.entry_type}: {self.amount} ({self.lease_id})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Ledger entries are immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Ledger entries are a permanent financial record and cannot be deleted.")
