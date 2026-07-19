"""
Development settings for TradeFlow.

Extends base settings for local development.
PostgreSQL is used in all environments per architecture decision.
"""

from .base import *  # noqa: F401, F403

# ------------------------------------------------------------------
# Security overrides for development
# ------------------------------------------------------------------
DEBUG = True
SECRET_KEY = "dev-secret-key-do-not-use-in-production"
ALLOWED_HOSTS = ["*"]

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------
# Default DATABASE_URL falls through to base - override here if needed
# for custom local PostgreSQL credentials.

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True  # Development only

# ------------------------------------------------------------------
# Email
# ------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["tradeflow"]["level"] = "DEBUG"  # noqa: F405

# ------------------------------------------------------------------
# DRF browsable API (development only)
# ------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# ------------------------------------------------------------------
# Dramatically reduce password validators for dev speed
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = []