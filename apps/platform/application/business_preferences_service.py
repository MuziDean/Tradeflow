"""
Application service for BusinessPreferences.

No domain events emitted (no state changes that require notification).
"""

from typing import Optional

from django.db import transaction

from apps.platform.domain.entities import BusinessPreferences
from apps.platform.infrastructure.repositories import BusinessPreferencesRepository


class BusinessPreferencesService:
    """Service for BusinessPreferences."""

    def __init__(self, prefs_repository: BusinessPreferencesRepository):
        self.prefs_repository = prefs_repository

    def get_preferences(self, tenant_id: str) -> Optional[BusinessPreferences]:
        return self.prefs_repository.get_for_tenant(tenant_id)

    def update_preferences(self, prefs: BusinessPreferences) -> BusinessPreferences:
        with transaction.atomic():
            return self.prefs_repository.create_or_update(prefs)