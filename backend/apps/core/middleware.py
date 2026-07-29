import logging
import uuid

from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.request_context import request_id_ctx

logger = logging.getLogger("apps.core")

_jwt_authenticator = JWTAuthentication()


class RequestIDMiddleware(MiddlewareMixin):
    """Attaches a unique id to every request, echoes it back as a response
    header, and exposes it to the logging formatter for correlation."""

    header_name = "X-Request-ID"

    def process_request(self, request):
        request_id = request.headers.get(self.header_name, str(uuid.uuid4()))
        request.request_id = request_id
        request_id_ctx.value = request_id

    def process_response(self, request, response):
        response[self.header_name] = getattr(request, "request_id", "-")
        return response


class CurrentOrganizationMiddleware(MiddlewareMixin):
    """Resolves the tenant ("organization") the request is acting on.

    The frontend sends the id of the organization the user currently has
    selected via the `X-Organization-ID` header. This middleware decodes the
    JWT (if present), verifies the user has an active membership in that
    organization, and attaches `request.organization` / `request.membership`
    so every downstream view/permission can scope queries without repeating
    that lookup.
    """

    def process_request(self, request):
        request.organization = None
        request.membership = None

        drf_request = Request(request, authenticators=[_jwt_authenticator])
        try:
            auth_result = _jwt_authenticator.authenticate(drf_request)
        except AuthenticationFailed:
            auth_result = None

        if auth_result is None:
            return

        user, _token = auth_result
        request.user = user

        organization_id = request.headers.get("X-Organization-ID")
        if not organization_id:
            return

        from apps.organizations.models import Membership

        membership = (
            Membership.objects.select_related("organization")
            .filter(
                user=user,
                organization_id=organization_id,
                is_active=True,
                organization__is_active=True,
            )
            .first()
        )
        if membership is not None:
            request.organization = membership.organization
            request.membership = membership
