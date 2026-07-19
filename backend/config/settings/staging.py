"""
Staging settings for TradeFlow.

Extends base settings for staging/pre-production environment.
Production-like configuration with relaxed security for testing.
"""

from .base import *  # noqa: F401, F403

# ------------------------------------------------------------------
# Security
# ------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["staging.tradeflow.co.za"])

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["https://staging.tradeflow.co.za"],
)

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
LOGGING["root"]["handlers"] = ["json"]  # noqa: F405
LOGGING["root"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["tradeflow"]["handlers"] = ["json"]  # noqa: F405

# ------------------------------------------------------------------
# Security
# ------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True