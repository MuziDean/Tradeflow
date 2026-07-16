"""
Domain event base class for TradeFlow.

Per SAD Section 7: Domain events represent business facts (immutable).
All domain events inherit from this base class.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class DomainEvent:
    """
    Base class for all domain events in TradeFlow.

    Domain events represent immutable business facts that have occurred.
    They are produced by application services after successful transaction
    commit and consumed by other modules or background workers.
    """

    event_id: str = field(default_factory=new_id_str)
    occurred_at: datetime = field(default_factory=now)
    tenant_id: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event for outbox persistence and message queue."""
        return {
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "tenant_id": self.tenant_id,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "event_type": self.__class__.__name__,
            "event_data": self.event_data,
        }

    @property
    def event_type(self) -> str:
        """Return the class name as the event type."""
        return self.__class__.__name__