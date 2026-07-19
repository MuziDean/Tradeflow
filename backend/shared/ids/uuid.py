"""
UUID generation utilities for TradeFlow.

Per Database Design: UUIDs are used for all primary keys instead of
auto-increment integers. PostgreSQL gen_random_uuid() is used for
performance and security.
"""

import uuid


def new_id() -> uuid.UUID:
    """Generate a new UUID v4 for use as a primary key."""
    return uuid.uuid4()


def new_id_str() -> str:
    """Generate a new UUID v4 as a string."""
    return str(uuid.uuid4())


def parse_id(value: str) -> uuid.UUID:
    """Parse a UUID string, raising ValueError if invalid."""
    return uuid.UUID(value)