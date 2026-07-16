"""
Health check endpoints for TradeFlow.

Provides liveness and readiness probes for container orchestration.
Per DevOps Architecture Section 8.1: Health checks must not overload dependencies.
"""

from django.db import connection
from django.http import JsonResponse


def health(request):
    """
    Liveness probe - returns 200 if the application process is running.
    Does not check dependencies to avoid cascading failures.
    """
    return JsonResponse({"status": "healthy", "service": "tradeflow-api"})


def readiness(request):
    """
    Readiness probe - checks that critical dependencies are reachable.
    Returns 200 when the app is ready to serve traffic.
    """
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {"status": "ready" if db_ok else "not_ready", "database": "ok" if db_ok else "unreachable"},
        status=status_code,
    )