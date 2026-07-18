"""
Application service for atomic document number generation.

Domain events emitted:
- NumberSequenceReset
"""

import logging

from django.db import transaction

from shared.events.number_sequence_events import NumberSequenceReset


logger = logging.getLogger("tradeflow.platform")


class NumberSequenceService:
    """Service for atomic document number generation."""

    def __init__(self, number_sequence_repository):
        self.number_sequence_repository = number_sequence_repository

    def get_next_number(self, tenant_id: str, name: str) -> str:
        """
        Return next formatted document number.
        Atomic via repository select_for_update.
        """
        with transaction.atomic():
            number = self.number_sequence_repository.get_next_number(tenant_id, name)
            seq = self.number_sequence_repository.get_by_name(tenant_id, name)
            formatted = f"{seq.prefix}{number:0{seq.padding_length}d}{seq.suffix}"
            return formatted

    def reset_sequence(self, tenant_id: str, name: str) -> bool:
        """Reset current_number to 1. Emits event."""
        with transaction.atomic():
            seq = self.number_sequence_repository.get_by_name(tenant_id, name)
            if not seq:
                return False
            seq.current_number = 1
            self.number_sequence_repository.create_or_update(seq)
            NumberSequenceReset(tenant_id=tenant_id, sequence_name=name).emit()
            return True