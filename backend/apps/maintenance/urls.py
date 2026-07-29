from rest_framework.routers import DefaultRouter

from apps.maintenance.views import MaintenanceRequestViewSet, VendorViewSet

router = DefaultRouter()
router.register("vendors", VendorViewSet, basename="vendor")
router.register("maintenance-requests", MaintenanceRequestViewSet, basename="maintenance-request")

urlpatterns = router.urls
