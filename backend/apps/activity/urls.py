from rest_framework.routers import DefaultRouter

from apps.activity.views import ActivityLogViewSet

router = DefaultRouter()
router.register("activity", ActivityLogViewSet, basename="activity")

urlpatterns = router.urls
