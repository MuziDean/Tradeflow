"""
Timezone-aware datetime utilities for TradeFlow.

Per base settings: TIME_ZONE = "Africa/Johannesburg"
All datetime handling must be timezone-aware using pytz.
"""

from datetime import datetime, timezone

from django.utils import timezone as django_tz


def now() -> datetime:
    """Return the current datetime in the default timezone (Africa/Johannesburg)."""
    return django_tz.now()


def now_utc() -> datetime:
    """Return the current datetime in UTC."""
    return datetime.now(tz=timezone.utc)


def to_sa_time(dt: datetime) -> datetime:
    """Convert a datetime to South Africa time (SAST)."""
    return dt.astimezone(django_tz.get_current_timezone())


def format_sa(dt: datetime) -> str:
    """Format a datetime for South Africa display."""
    return to_sa_time(dt).strftime("%Y-%m-%d %H:%M:%S SAST")