from corsheaders.defaults import default_headers

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

INSTALLED_APPS += ["django_extensions"]  # noqa: F405

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Local development can fall back to SQLite-free Postgres already configured
# in base.py; nothing to override there. Loosen CORS for local tooling.
CORS_ALLOW_ALL_ORIGINS = env.bool("DJANGO_CORS_ALLOW_ALL", default=True)
# `ng serve` (localhost:4200) and `manage.py runserver` (localhost:8000) are
# different origins, so the multi-tenancy header needs to be explicitly
# allowed or every request preflight-fails before CurrentOrganizationMiddleware
# ever sees it.
CORS_ALLOW_HEADERS = [*default_headers, "x-organization-id"]
