"""
API views for the IAM module.

Per Auth Spec §3: Endpoint contracts, validation, error codes.
Per Security Architecture: Rate limiting, lockout, tenant isolation, audit events.
Per Backend Engineering Standards §5.1: Thin views.
"""

import logging
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.iam.api.serializers import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)
from apps.iam.application.services import AuthenticationService, PasswordService, TokenService
from apps.iam.infrastructure.repositories import (
    PasswordResetRepository,
    SecurityEventRepository,
    UserRepository,
)
from apps.iam.infrastructure.redis_repositories import RateLimitRepository, SessionRepository

logger = logging.getLogger("tradeflow.auth")

# Endpoint-specific rate limits per Auth Spec §3 and Security §8.3
RATE_LIMITS = {
    "register": {"limit": 20, "window": 15 * 60},  # 20 per 15 min per IP
    "login": {"limit": 100, "window": 15 * 60},  # 100 per 15 min per IP
    "token_refresh": {"limit": 100, "window": 15 * 60},  # 100 per 15 min per IP
    "logout": {"limit": 200, "window": 15 * 60},  # 200 per 15 min per IP
    "password_reset": {"limit": 20, "window": 15 * 60},  # 20 per 15 min per IP
    "password_reset_confirm": {"limit": 50, "window": 15 * 60},  # 50 per 15 min per IP
}


class RegisterView(APIView):
    """
    POST /api/v1/auth/register

    Public endpoint. Tenant context resolved from host.
    Creates a new user within the current tenant.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["register"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:register", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]
        display_name = serializer.validated_data.get("display_name", "")

        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_service = AuthenticationService(
                user_repository=UserRepository(),
                security_event_repository=SecurityEventRepository(),
            )
            user = user_service.register(
                tenant_id=tenant_id,
                email=email,
                password=password,
                display_name=display_name,
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                request_id=getattr(request, "request_id", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Security event: AUTH_REGISTERED
        SecurityEventRepository().log_event(
            tenant_id=tenant_id,
            event_type="AUTH_REGISTERED",
            user_id=str(user.id),
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        return Response({"data": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/v1/auth/login

    Public endpoint. Authenticates user and issues access JWT + refresh session.
    Per Auth Spec §3.1: Rate limited, progressive delays, lockout enforced.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["login"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:login", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]
        remember_me = serializer.validated_data.get("remember_me", False)
        device_info = request.data.get("device", {})

        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService(
            user_repository=UserRepository(),
            security_event_repository=SecurityEventRepository(),
        )
        user = auth_service.authenticate(
            tenant_id=tenant_id,
            email=email,
            password=password,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        if user is None:
            return Response({"error": "AUTH_INVALID_CREDENTIALS"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_locked:
            return Response({"error": "AUTH_ACCOUNT_LOCKED"}, status=status.HTTP_423_LOCKED)

        # Create refresh session
        session_repo = SessionRepository()
        session_id, refresh_token, family_id = session_repo.create(
            tenant_id=tenant_id,
            user_id=str(user.id),
            device_info=device_info,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            remember_me=remember_me,
        )

        # Create access JWT
        token_service = TokenService(user_repository=UserRepository())
        access_token = token_service.create_access_token(user, session_id)

        response_data = {
            "data": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "display_name": user.display_name,
                    "company_id": str(user.tenant_id),
                },
                "session": {"session_id": session_id, "expires_at": (timezone.now() + timedelta(days=7 if not remember_me else 30)).isoformat()},
            }
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60 if not remember_me else 30 * 24 * 60 * 60,
            path="/api/v1/auth/token/refresh",
        )
        return response


class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/token/refresh

    Rotate refresh token and issue new access JWT.
    Per Auth Spec §3.2: Replay detection revokes session family.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["token_refresh"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:token_refresh", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        refresh_token = request.COOKIES.get("refresh_token") or request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "AUTH_REFRESH_INVALID"}, status=status.HTTP_401_UNAUTHORIZED)

        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "TENANT_MISMATCH"}, status=status.HTTP_403_FORBIDDEN)

        session_repo = SessionRepository()
        matched = None
        user_id = None

        if request.user.is_authenticated:
            user_id = str(request.user.id)
            sessions = session_repo.list_for_user(tenant_id, user_id)
            for s in sessions:
                if s.get("refresh_token_hash") == refresh_token:
                    matched = s
                    break

        if matched is None:
            return Response({"error": "AUTH_REFRESH_INVALID"}, status=status.HTTP_401_UNAUTHORIZED)

        if matched.get("revoked"):
            session_repo.revoke_all_for_user(tenant_id, matched["user_id"])
            SecurityEventRepository().log_event(
                tenant_id=tenant_id,
                event_type="AUTH_REFRESH_REPLAY_DETECTED",
                user_id=matched["user_id"],
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                request_id=getattr(request, "request_id", ""),
            )
            return Response({"error": "AUTH_REFRESH_REPLAY_DETECTED"}, status=status.HTTP_409_CONFLICT)

        # Rotate: revoke old session, create new one
        session_repo.revoke(tenant_id, matched["session_id"])

        user = UserAccount(id=matched["user_id"], tenant_id=matched["tenant_id"], email="")
        token_service = TokenService(user_repository=UserRepository())
        new_session_id, new_refresh_token, _ = session_repo.create(
            tenant_id=matched["tenant_id"],
            user_id=matched["user_id"],
            device_info=matched.get("device_info", {}),
            ip_address=matched.get("ip_address", ""),
            user_agent=matched.get("user_agent", ""),
        )
        access_token = token_service.create_access_token(user, new_session_id)

        SecurityEventRepository().log_event(
            tenant_id=matched["tenant_id"],
            event_type="AUTH_TOKEN_REFRESHED",
            user_id=matched["user_id"],
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        response_data = {
            "data": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                "session_id": new_session_id,
            }
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
            path="/api/v1/auth/token/refresh",
        )
        return response


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout

    Revoke current refresh session. Idempotent.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["logout"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:logout", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        refresh_token = request.COOKIES.get("refresh_token")
        tenant_id = getattr(request.actor, "tenant_id", None)
        user_id = str(request.user.id)

        if refresh_token and tenant_id:
            session_repo = SessionRepository()
            sessions = session_repo.list_for_user(tenant_id, user_id)
            for s in sessions:
                if s.get("refresh_token_hash") == refresh_token:
                    session_repo.revoke(tenant_id, s["session_id"])
                    break

        SecurityEventRepository().log_event(
            tenant_id=tenant_id or "",
            event_type="AUTH_LOGOUT",
            user_id=user_id,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        response = Response({"data": {"logged_out": True}})
        response.delete_cookie("refresh_token", path="/api/v1/auth/token/refresh")
        return response


class CurrentUserView(APIView):
    """
    GET /api/v1/auth/me

    Return authenticated user profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = UserSerializer({
            "id": str(user.id),
            "email": user.email,
            "display_name": getattr(user, "display_name", ""),
            "status": getattr(user, "status", ""),
            "last_login_at": getattr(user, "last_login_at", None),
        })

        return Response({
            "data": {
                "user": serializer.data,
                "company_id": str(getattr(request.actor, "tenant_id", "")),
            }
        })


class PasswordResetView(APIView):
    """
    POST /api/v1/auth/password/reset

    Public endpoint. Initiate password reset.
    Per Security §3.6: Do not reveal account existence.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["password_reset"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:password_reset", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        tenant_id = getattr(request.actor, "tenant_id", None)

        password_service = PasswordService(
            password_reset_repository=PasswordResetRepository(),
            security_event_repository=SecurityEventRepository(),
        )
        token, raw_token = password_service.request_reset(
            tenant_id=tenant_id or "",
            email=email,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        # Security event: AUTH_PASSWORD_RESET_REQUESTED
        if token:
            SecurityEventRepository().log_event(
                tenant_id=str(token.tenant_id),
                event_type="AUTH_PASSWORD_RESET_REQUESTED",
                user_id=str(token.user_id),
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                request_id=getattr(request, "request_id", ""),
            )

        # TODO: Send email with reset link containing raw_token
        # For now, return the token in response (development only)
        if token:
            logger.info("Password reset token for %s: %s (email delivery not configured)", email, raw_token)

        return Response({"data": {"reset_requested": True}})


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password/reset/confirm

    Public endpoint. Complete password reset using token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "")
        rl = RATE_LIMITS["password_reset_confirm"]
        rate_repo = RateLimitRepository()
        allowed, remaining = rate_repo.check_and_increment(
            category="auth:password_reset_confirm", identifier=ip, limit=rl["limit"], window_seconds=rl["window"]
        )
        if not allowed:
            return Response({"error": "RATE_LIMIT_EXCEEDED"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_id = serializer.validated_data["token"]
        raw_token = serializer.validated_data["token"]  # In real flow, raw_token comes from URL/email
        new_password = serializer.validated_data["new_password"]

        password_service = PasswordService(
            password_reset_repository=PasswordResetRepository(),
            security_event_repository=SecurityEventRepository(),
        )
        user = password_service.confirm_reset(
            token_id=token_id,
            raw_token=raw_token,
            new_password=new_password,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        if user is None:
            SecurityEventRepository().log_event(
                tenant_id="",
                event_type="AUTH_RESET_TOKEN_INVALID_OR_EXPIRED",
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                request_id=getattr(request, "request_id", ""),
            )
            return Response({"error": "AUTH_RESET_TOKEN_INVALID_OR_EXPIRED"}, status=status.HTTP_401_UNAUTHORIZED)

        # Revoke all sessions for user (security best practice after password change)
        if user.tenant_id:
            session_repo = SessionRepository()
            session_repo.revoke_all_for_user(str(user.tenant_id), str(user.id))

        SecurityEventRepository().log_event(
            tenant_id=str(user.tenant_id),
            event_type="AUTH_PASSWORD_RESET_COMPLETED",
            user_id=str(user.id),
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_id=getattr(request, "request_id", ""),
        )

        return Response({"data": {"password_reset": True}})