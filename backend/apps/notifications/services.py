from apps.core.permissions import ROLE_HIERARCHY
from apps.notifications.models import Notification


def notify_user(user, *, organization, notification_type, title, body="", link=""):
    if user is None:
        return None
    return Notification.objects.create(
        organization=organization,
        recipient=user,
        notification_type=notification_type,
        title=title,
        body=body,
        link=link,
    )


def notify_organization_roles(organization, *, min_role, notification_type, title, body="", link="", exclude_user=None):
    """Notifies every active member whose role is at or above `min_role`.
    Used for organization-wide events (e.g. a new maintenance request)
    rather than events scoped to a single tenant.
    """
    from apps.organizations.models import Membership

    threshold = ROLE_HIERARCHY.get(min_role, 0)
    eligible_roles = [role for role, level in ROLE_HIERARCHY.items() if level >= threshold]

    memberships = Membership.objects.filter(
        organization=organization, is_active=True, role__in=eligible_roles
    ).select_related("user")

    notifications = [
        Notification(
            organization=organization,
            recipient=membership.user,
            notification_type=notification_type,
            title=title,
            body=body,
            link=link,
        )
        for membership in memberships
        if exclude_user is None or membership.user_id != exclude_user.id
    ]
    return Notification.objects.bulk_create(notifications)
