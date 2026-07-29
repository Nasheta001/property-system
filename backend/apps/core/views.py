from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Liveness/readiness probe used by Docker, load balancers and uptime
    monitors. Verifies the process can actually reach its dependencies
    rather than just returning 200 unconditionally.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        checks = {"database": self._check_database(), "cache": self._check_cache()}
        healthy = all(checks.values())
        return Response({"status": "ok" if healthy else "degraded", "checks": checks}, status=200 if healthy else 503)

    @staticmethod
    def _check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except OperationalError:
            return False

    @staticmethod
    def _check_cache():
        try:
            marker = "health-check-probe"
            cache.set(marker, "1", timeout=5)
            return cache.get(marker) == "1"
        except Exception:
            return False
