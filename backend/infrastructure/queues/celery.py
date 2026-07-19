"""
Celery configuration for TradeFlow.

Per SAD Section 8: Celery workers consume outbox events and perform
side effects (notifications, exports, PDFs, scheduled reports).
Priority queues ensure critical jobs (payroll) run before low-priority ones.
"""

import logging
import os

from celery import Celery
from django.conf import settings

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("tradeflow")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True, name="health_check")
def health_check(self):
    """Celery health check task."""
    return {"status": "ok", "task_id": self.request.id}