"""
Application service for global Currency (read-only except admin seed).

No domain events emitted (seed/read operations only).
"""

from typing import Optional

from apps.platform.domain.entities import Currency
from apps.platform.infrastructure.repositories import CurrencyRepository


class CurrencyService:
    """Service for global Currency (read-only except admin seed)."""

    def __init__(self, currency_repository: CurrencyRepository):
        self.currency_repository = currency_repository

    def list_currencies(self) -> list[Currency]:
        return self.currency_repository.list_all()

    def get_currency(self, code: str) -> Optional[Currency]:
        return self.currency_repository.get_by_code(code)

    def seed_currencies(self, currencies: list[Currency]) -> None:
        """Admin operation: seed ISO 4217 currencies."""
        self.currency_repository.bulk_create(currencies)