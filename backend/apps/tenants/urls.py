from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantProfileViewSet

router = DefaultRouter()
router.register("tenants", TenantProfileViewSet, basename="tenant")

urlpatterns = router.urls
