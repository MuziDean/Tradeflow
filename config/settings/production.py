"""
Production settings for TradeFlow.

Extends base settings for production environment.
All security hardening is enabled. Secrets come from environment variables.
"""

from .base import *  # noqa: F401, F403

# ------------------------------------------------------------------
# Security
# ------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["tradeflow.co.za", "api.tradeflow.co.za"])
SECRET_KEY = env("SECRET_KEY")

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["https://tradeflow.co.za", "https://app.tradeflow.co.za"],
)

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
LOGGING["root"]["handlers"] = ["json"]  # noqa: F405
LOGGING["root"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["tradeflow"]["handlers"] = ["json"]  # noqa: F405

# ------------------------------------------------------------------
# Security hardening
# ------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ------------------------------------------------------------------
# Database connection pooling
# ------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
DATABASES["default"]["OPTIONS"] = {  # noqa: F405
    "pool": True,
    "connect_timeout": 10,
}

# ------------------------------------------------------------------
# Static files
# ------------------------------------------------------------------
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"