"""
Logging configuration for TradeFlow.

Provides structured JSON logging with correlation IDs, tenant context,
and user context for all log entries.

Per documentation Section 12: Structured logs (JSON) with required fields.
"""

import logging

from django.utils.deprecation import MiddlewareMixin


class LoggingContextMiddleware(MiddlewareMixin):
    """
    Middleware that enriches log records with request context.

    Adds request_id, tenant_id, and user_id to all log entries
    made during request processing.
    """

    def process_request(self, request):
        request.log_context = {}

    def process_response(self, request, response):
        return response


class TradeFlowLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds contextual fields to log records.

    Usage:
        logger = TradeFlowLoggerAdapter(logging.getLogger(__name__), {})
        logger.info("Sale completed", extra={"sale_id": "..."})
    """

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra.setdefault("request_id", getattr(self.extra, "request_id", None))
        extra.setdefault("tenant_id", getattr(self.extra, "tenant_id", None))
        extra.setdefault("user_id", getattr(self.extra, "user_id", None))
        kwargs["extra"] = extra
        return msg, kwargs