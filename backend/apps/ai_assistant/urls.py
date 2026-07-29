from rest_framework.routers import DefaultRouter

from apps.ai_assistant.views import AIConversationViewSet

router = DefaultRouter()
router.register("ai/conversations", AIConversationViewSet, basename="ai-conversation")

urlpatterns = router.urls
