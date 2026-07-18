"""
Number sequence domain events.

Emitted by NumberSequenceService on state changes.
"""

from shared.events.base import DomainEvent


class NumberSequenceReset(DomainEvent):
    def __init__(self, tenant_id: str, sequence_name: str):
        super().__init__(
            "number_sequence.reset",
            {"tenant_id": tenant_id, "sequence_name": sequence_name},
        )