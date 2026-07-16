"""
Request ID middleware.

Generates and attaches a unique correlation ID to every request for
distributed tracing across logs, outbox events, and background jobs.
"""

import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """Attaches a unique request ID to each request for tracing."""

    def process_request(self, request):
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response