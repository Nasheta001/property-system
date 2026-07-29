from rest_framework import serializers

from apps.ai_assistant.models import AIConversation, AIMessage


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ["id", "role", "content", "provider", "created_at"]
        read_only_fields = fields


class AIConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AIConversation
        fields = ["id", "title", "message_count", "created_at", "updated_at"]
        read_only_fields = fields

    def get_message_count(self, obj):
        return obj.messages.count()


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000, trim_whitespace=True)

    def validate_question(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        return value
