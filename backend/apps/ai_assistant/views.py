from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ai_assistant.models import AIConversation
from apps.ai_assistant.serializers import AIConversationSerializer, AIMessageSerializer, AskQuestionSerializer
from apps.ai_assistant.services import ask, start_conversation
from apps.core.viewsets import TenantScopedModelViewSet


class AIConversationViewSet(TenantScopedModelViewSet):
    """A user's own conversations with the assistant — scoped to both the
    organization and the requesting user, since this is a personal working
    tool rather than a shared team resource.
    """

    serializer_class = AIConversationSerializer
    queryset = AIConversation.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(started_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            started_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        if request.method == "POST":
            serializer = AskQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            message = ask(request.organization, request.user, conversation, serializer.validated_data["question"])
            return Response(AIMessageSerializer(message).data, status=201)

        return Response(AIMessageSerializer(conversation.messages.all(), many=True).data)

    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation, message = start_conversation(
            request.organization, request.user, serializer.validated_data["question"]
        )
        return Response(
            {
                "conversation": AIConversationSerializer(conversation).data,
                "message": AIMessageSerializer(message).data,
            },
            status=201,
        )
