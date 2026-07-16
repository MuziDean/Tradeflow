"""
Test settings for TradeFlow.

Extends base settings for running automated tests.
Uses PostgreSQL in Docker (no SQLite) with fast test configuration.
"""

from .base import *  # noqa: F401, F403

# ------------------------------------------------------------------
# Security
# ------------------------------------------------------------------
DEBUG = False
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------
# Use PostgreSQL from docker-compose for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tradeflow_test",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
    }
}

# ------------------------------------------------------------------
# Password hashers (fast for tests)
# ------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ------------------------------------------------------------------
# Email
# ------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = ["http://testserver"]

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
import logging  # noqa: E402

logging.disable(logging.CRITICAL)

# ------------------------------------------------------------------
# Cache
# ------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# ------------------------------------------------------------------
# Celery (run tasks synchronously in tests)
# ------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ------------------------------------------------------------------
# Storage
# ------------------------------------------------------------------
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ------------------------------------------------------------------
# DRF
# ------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
)
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405