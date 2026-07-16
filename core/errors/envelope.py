"""
Standard error envelope for TradeFlow API responses.

Per API Specification: Consistent error format with code, message, field,
and correlation_id. Never leak stack traces or internal details.
"""

import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("tradeflow.errors")


class TradeFlowError(APIException):
    """Base exception for TradeFlow business rule violations."""

    default_code = "INTERNAL_ERROR"
    default_message = "An unexpected error occurred."

    def __init__(self, message=None, code=None, field=None):
        self.detail = message or self.default_message
        self.code = code or self.default_code
        self.field = field

    def get_full_details(self):
        return {
            "code": self.code,
            "message": str(self.detail),
            "field": self.field,
        }


class BusinessRuleViolation(TradeFlowError):
    """Raised when a business rule is violated (e.g., insufficient stock, locked payroll)."""

    default_code = "BUSINESS_RULE_VIOLATION"
    default_message = "Operation violates a business rule."


class InsufficientStock(BusinessRuleViolation):
    default_code = "INSUFFICIENT_STOCK"
    default_message = "Insufficient stock available."


class TenantConflict(TradeFlowError):
    default_code = "TENANT_CONFLICT"
    default_message = "Cross-tenant access denied."


def exception_handler(exc, context):
    """
    Standard DRF exception handler that returns a consistent error envelope.

    Per API Specification:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "field": "field_name" (optional)
        }
    }
    """
    request = context.get("request")
    correlation_id = getattr(request, "request_id", None) if request else None

    # Handle TradeFlow custom exceptions
    if isinstance(exc, TradeFlowError):
        return Response(
            {
                "success": False,
                "error": exc.get_full_details(),
                "correlation_id": correlation_id,
            },
            status=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
        )

    # Let DRF handle standard exceptions
    response = drf_exception_handler(exc, context)
    if response is not None:
        # Wrap in standard envelope
        data = response.data
        error = {
            "code": getattr(exc, "default_code", "ERROR"),
            "message": str(data.get("detail", str(exc))),
        }
        if isinstance(data, dict):
            field_errors = {k: v for k, v in data.items() if k != "detail"}
            if field_errors:
                error["field_errors"] = field_errors

        response.data = {
            "success": False,
            "error": error,
            "correlation_id": correlation_id,
        }
        return response

    # Unknown errors - log and return generic message
    logger.exception("Unhandled exception")
    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
            "correlation_id": correlation_id,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )