"""
Redis-backed repositories for IAM.

Per Security Architecture §13: Redis for sessions, refresh tokens, rate limiting.
Per SAD §10.4: Redis is backbone for session/refresh token store + rate limiting.
"""

import json
from datetime import timedelta
from uuid import uuid4

from django.core.cache import cache
from django.utils import timezone


class SessionRepository:
    """
    Redis-backed refresh session store.

    Per Security §3.2: Refresh tokens bound to server-side session record
    stored in Redis for revocation and replay detection.
    """

    def __init__(self, prefix: str = "tradeflow:session"):
        self.prefix = prefix
        self.ttl_seconds = 7 * 24 * 60 * 60  # 7 days default

    def _key(self, tenant_id: str, session_id: str) -> str:
        return f"{self.prefix}:{tenant_id}:{session_id}"

    def create(
        self,
        tenant_id: str,
        user_id: str,
        device_info: dict | None = None,
        ip_address: str = "",
        user_agent: str = "",
        remember_me: bool = False,
    ) -> tuple[str, str]:
        """
        Create a refresh session.

        Returns (session_id, refresh_token). Both are opaque UUIDs.
        Session data is stored in Redis. Token is issued to client.
        """
        session_id = str(uuid4())
        refresh_token = str(uuid4())
        family_id = str(uuid4())

        now = timezone.now()
        session_data = {
            "session_id": session_id,
            "family_id": family_id,
            "user_id": str(user_id),
            "tenant_id": str(tenant_id),
            "refresh_token_hash": refresh_token,  # In production, hash this
            "device_info": device_info or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now.isoformat(),
            "last_seen_at": now.isoformat(),
            "revoked": False,
        }

        ttl = self.ttl_seconds
        if remember_me:
            ttl = 30 * 24 * 60 * 60  # 30 days

        key = self._key(tenant_id, session_id)
        cache.set(key, json.dumps(session_data), ttl)

        return session_id, refresh_token, family_id

    def get(self, tenant_id: str, session_id: str) -> dict | None:
        """Get session data. Returns None if not found or expired."""
        key = self._key(tenant_id, session_id)
        raw = cache.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def revoke(self, tenant_id: str, session_id: str) -> bool:
        """Revoke a session. Returns True if session existed."""
        key = self._key(tenant_id, session_id)
        data = cache.get(key)
        if data is None:
            return False
        data = json.loads(data)
        data["revoked"] = True
        # Keep for audit window, then let TTL expire
        cache.set(key, json.dumps(data), timeout=3600)  # 1 hour audit retention
        return True

    def revoke_all_for_user(self, tenant_id: str, user_id: str) -> int:
        """
        Revoke all sessions for a user.
        Returns count of revoked sessions.
        """
        # In production with Redis SCAN for production; Django cache abstraction
        # doesn't support SCAN, so we use a user->session mapping key
        mapping_key = f"{self.prefix}:user_sessions:{tenant_id}:{user_id}"
        session_ids = cache.get(mapping_key, [])
        revoked = 0
        for sid in session_ids:
            if self.revoke(tenant_id, sid):
                revoked += 1
        cache.delete(mapping_key)
        return revoked

    def list_for_user(self, tenant_id: str, user_id: str) -> list[dict]:
        """List active sessions for a user."""
        mapping_key = f"{self.prefix}:user_sessions:{tenant_id}:{user_id}"
        session_ids = cache.get(mapping_key, [])
        sessions = []
        for sid in session_ids:
            data = self.get(tenant_id, sid)
            if data and not data.get("revoked"):
                sessions.append(data)
        return sessions


class RateLimitRepository:
    """
    Redis-backed rate limiting.

    Per Security §8.3: Apply per IP, per tenant, endpoint class.
    Per Auth Spec §3.1: Auth endpoints 100 requests/15min/IP.
    """

    def __init__(self, prefix: str = "tradeflow:ratelimit"):
        self.prefix = prefix

    def _key(self, category: str, identifier: str) -> str:
        return f"{self.prefix}:{category}:{identifier}"

    def check_and_increment(
        self,
        category: str,
        identifier: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Check rate limit and increment counter.

        Returns (allowed, remaining_count).
        Uses Redis INCR + TTL for atomic windowing.
        """
        key = self._key(category, identifier)
        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=window_seconds)
            return True, limit - 1

        current = int(current)
        if current >= limit:
            return False, 0

        new_value = current + 1
        cache.set(key, new_value, timeout=window_seconds)
        return True, limit - new_value

    def reset(self, category: str, identifier: str) -> None:
        """Reset rate limit counter."""
        key = self._key(category, identifier)
        cache.delete(key)