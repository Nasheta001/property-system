from rest_framework.routers import DefaultRouter

from apps.payments.views import LedgerEntryViewSet, PaymentViewSet

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")
router.register("ledger-entries", LedgerEntryViewSet, basename="ledger-entry")

urlpatterns = router.urls
