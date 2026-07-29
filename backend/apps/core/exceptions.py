import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("apps.core")


def custom_exception_handler(exc, context):
    """Normalizes every DRF error response to a single, predictable shape:

        {"error": {"code": "validation_error", "message": "...", "details": {...}}}

    so frontend error handling never has to special-case a given endpoint.
    """
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception", exc_info=exc)
        return Response(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again.",
                    "details": {},
                }
            },
            status=500,
        )

    code = getattr(exc, "default_code", "error")
    if isinstance(response.data, dict) and not isinstance(exc, drf_exceptions.ValidationError):
        message = response.data.get("detail", str(exc))
        details = {k: v for k, v in response.data.items() if k != "detail"}
    elif isinstance(response.data, dict):
        message = "Validation failed."
        details = response.data
    else:
        message = "Validation failed."
        details = {"non_field_errors": response.data}

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
