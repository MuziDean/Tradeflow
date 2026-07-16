"""
Outbox pattern implementation for TradeFlow.

Per SAD Section 7.3: Domain events are persisted via Outbox pattern so that
"commit + publish" is reliable. Celery consumes outbox to deliver events.
"""

from django.db import models
from shared.ids.uuid import new_id_str


class OutboxEvent(models.Model):
    """
    Persistent record of domain events to be published.

    Events are written in the same transaction as the business state change
    and consumed by Celery workers for reliable delivery.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    tenant_id = models.CharField(max_length=36, db_index=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    occurred_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "outbox_events"
        indexes = [
            models.Index(fields=["tenant_id", "occurred_at"]),
            models.Index(fields=["published_at"]),
        ]
        ordering = ["occurred_at"]  # noqa: A003

    def __str__(self) -> str:
        return f"{self.event_type} [{self.tenant_id}] {self.occurred_at}"