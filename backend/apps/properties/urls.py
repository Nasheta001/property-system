from rest_framework.routers import DefaultRouter

from apps.properties.views import BuildingViewSet, FloorViewSet, PropertyViewSet, UnitViewSet

router = DefaultRouter()
router.register("properties", PropertyViewSet, basename="property")
router.register("buildings", BuildingViewSet, basename="building")
router.register("floors", FloorViewSet, basename="floor")
router.register("units", UnitViewSet, basename="unit")

urlpatterns = router.urls
