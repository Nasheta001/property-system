"""Lightweight module holding request-scoped state for log correlation.

Kept dependency-free (no DRF / simplejwt imports) because Django's LOGGING
dictConfig resolves this filter during `django.setup()`, before the app
registry is ready — importing anything that touches `django.contrib.auth`
at that point raises `AppRegistryNotReady`.
"""
import logging


class _RequestIDContext:
    value = "-"


request_id_ctx = _RequestIDContext()


class RequestIDLogFilter(logging.Filter):
    """Injects the current request id into every log record so requests can
    be traced end-to-end across the JSON logs."""

    def filter(self, record):
        record.request_id = request_id_ctx.value
        return True
