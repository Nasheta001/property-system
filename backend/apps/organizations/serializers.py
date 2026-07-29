from django.db import transaction
from rest_framework import serializers

from apps.organizations.models import Membership, Organization
from apps.users.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "subscription_plan",
            "is_active",
            "email",
            "phone_number",
            "address",
            "city",
            "country",
            "timezone",
            "currency",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "subscription_plan", "is_active", "created_at"]

    def get_role(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return None
        membership = next((m for m in getattr(obj, "_prefetched_memberships", []) if m.user_id == request.user.id), None)
        if membership is not None:
            return membership.role
        membership = obj.memberships.filter(user=request.user, is_active=True).first()
        return membership.role if membership else None

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        organization = Organization.objects.create(owner=request.user, created_by=request.user, **validated_data)
        Membership.objects.create(
            organization=organization,
            user=request.user,
            role=Membership.Role.OWNER,
            created_by=request.user,
        )
        return organization


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Membership._meta.get_field("user").related_model.objects.all(),
        source="user",
        write_only=True,
    )

    class Meta:
        model = Membership
        fields = ["id", "organization", "user", "user_id", "role", "is_active", "joined_at", "created_at"]
        read_only_fields = ["id", "organization", "joined_at", "created_at"]
