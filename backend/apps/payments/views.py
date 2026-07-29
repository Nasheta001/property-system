from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.core.permissions import HasOrganizationRole
from apps.core.viewsets import TenantScopedModelViewSet, TenantScopedReadOnlyModelViewSet
from apps.payments.models import LedgerEntry, Payment
from apps.payments.serializers import LedgerEntrySerializer, PaymentSerializer, PaymentTransitionSerializer
from apps.payments.services import (
    PaymentTransitionError,
    cancel_payment,
    mark_payment_failed,
    mark_payment_paid,
    refund_payment,
)


class PaymentViewSet(TenantScopedModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [HasOrganizationRole]
    required_role = "accountant"
    queryset = Payment.objects.select_related("lease", "lease__unit", "tenant")
    filterset_fields = ["status", "method", "lease", "tenant"]
    search_fields = ["receipt_number", "provider_reference", "tenant__first_name", "tenant__last_name"]
    ordering_fields = ["payment_date", "created_at", "amount"]

    def perform_create(self, serializer):
        lease = serializer.validated_data["lease"]
        serializer.save(
            organization=self.request.organization,
            tenant=lease.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_destroy(self, instance):
        if instance.status in (Payment.Status.PAID, Payment.Status.SETTLED, Payment.Status.REFUNDED):
            raise DRFValidationError(
                {"detail": "Completed payments are part of the permanent financial record and cannot be deleted."}
            )
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = mark_payment_paid(
                payment, request.user, provider_reference=serializer.validated_data.get("provider_reference", "")
            )
        except PaymentTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def mark_failed(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = mark_payment_failed(payment, request.user, reason=serializer.validated_data.get("reason", ""))
        except PaymentTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        payment = self.get_object()
        try:
            payment = cancel_payment(payment, request.user)
        except PaymentTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = refund_payment(payment, request.user, reason=serializer.validated_data.get("reason", ""))
        except PaymentTransitionError as exc:
            raise DRFValidationError({"detail": str(exc)})
        return Response(self.get_serializer(payment).data)


class LedgerEntryViewSet(TenantScopedReadOnlyModelViewSet):
    serializer_class = LedgerEntrySerializer
    queryset = LedgerEntry.objects.select_related("lease", "lease__unit", "lease__tenant", "payment")
    filterset_fields = ["entry_type", "lease", "payment"]
    ordering_fields = ["created_at", "amount"]
