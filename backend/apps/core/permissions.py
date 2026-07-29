from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    """Grants access only to authenticated users with an active membership
    in the organization resolved onto the request by
    `CurrentOrganizationMiddleware` (see apps.core.middleware).
    """

    message = "You are not a member of this organization."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.organization is not None)

    def has_object_permission(self, request, view, obj):
        organization_id = getattr(obj, "organization_id", None) or getattr(obj, "id", None)
        return organization_id == request.organization.id


ROLE_HIERARCHY = {
    "owner": 100,
    "admin": 90,
    "property_manager": 70,
    "landlord": 60,
    "accountant": 50,
    "auditor": 40,
    "vendor": 30,
    "tenant": 20,
}


class HasOrganizationRole(BasePermission):
    """Restricts write access to members whose role meets `required_role`
    (or above, per ROLE_HIERARCHY) on the view. Read access is always
    allowed to any organization member.

    Usage: set `required_role = "admin"` as a class attribute on the view.
    """

    def has_permission(self, request, view):
        if not IsOrganizationMember().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        required_role = getattr(view, "required_role", "admin")
        membership = getattr(request, "membership", None)
        if membership is None:
            return False
        return ROLE_HIERARCHY.get(membership.role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
