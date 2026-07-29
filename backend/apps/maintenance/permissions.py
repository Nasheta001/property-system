from apps.core.permissions import ROLE_HIERARCHY, IsOrganizationMember

# Anyone in the organization — including a tenant — may report an issue,
# read requests, and add comments/attachments as it progresses. Only these
# actions actually drive the workflow forward or edit/delete a request, so
# only these are gated behind a landlord-and-up role.
ELEVATED_ACTIONS = {
    "update",
    "partial_update",
    "destroy",
    "verify",
    "assign",
    "accept",
    "start_progress",
    "wait_for_parts",
    "complete",
    "review",
    "close",
}


class MaintenanceRequestPermission(IsOrganizationMember):
    """Any organization member (including a tenant) can report and read
    maintenance requests, and comment/attach evidence — that's the point
    of a `reported` request. Driving the workflow forward (verifying,
    assigning a vendor, closing it out) or editing/deleting a request is
    restricted to landlord-and-up roles, the same threshold used for
    leases and tenant profiles.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if view.action not in ELEVATED_ACTIONS:
            return True

        membership = getattr(request, "membership", None)
        if membership is None:
            return False
        return ROLE_HIERARCHY.get(membership.role, 0) >= ROLE_HIERARCHY.get("landlord", 0)
