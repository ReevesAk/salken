import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)

HEALTH_PATH = '/health/'


# HealthCheckMiddleware answers load balancer health checks at /health/.
# It runs before host validation, because health checks are addressed to the
# instance IP, which is not in ALLOWED_HOSTS. Returns 503 when the database
# is unreachable.
class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != HEALTH_PATH:
            return self.get_response(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        except DatabaseError:
            logger.exception('Health check failed: database unavailable')
            return JsonResponse({'status': 'error', 'database': 'unavailable'}, status=503)
        return JsonResponse({'status': 'ok', 'database': 'ok'})
