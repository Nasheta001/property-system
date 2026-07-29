from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.platform_admin.views import PlatformOrganizationViewSet, PlatformStatsView

router = DefaultRouter()
router.register("platform/organizations", PlatformOrganizationViewSet, basename="platform-organization")

urlpatterns = [
    path("platform/stats/", PlatformStatsView.as_view(), name="platform-stats"),
] + router.urls
