from rest_framework.permissions import BasePermission


class IsPlatformStaff(BasePermission):
    """The platform-owner tier sits above every organization: staff see
    across tenant boundaries by design, gated on `User.is_staff` (already
    used to control Django admin access) rather than any organization
    membership or role.
    """

    message = "Platform staff access is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
