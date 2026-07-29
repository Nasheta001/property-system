from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.subscriptions.views import CurrentSubscriptionView, PlanListView, SubscriptionEventViewSet

router = DefaultRouter()
router.register("subscriptions/events", SubscriptionEventViewSet, basename="subscription-event")

urlpatterns = [
    path("subscriptions/plans/", PlanListView.as_view(), name="subscription-plans"),
    path("subscriptions/current/", CurrentSubscriptionView.as_view(), name="subscription-current"),
] + router.urls
