"""PAT autentifikatsiyasi — ADR-0008."""

from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import authentication, exceptions

from core.models import ApiToken, User


class ApiTokenAuthentication(authentication.BaseAuthentication):
    """`Authorization: Bearer rw_...`

    Token bazada hash bo'yicha qidiriladi — ochiq qiymat saqlanmaydi.
    """

    keyword = "Bearer"

    def authenticate(self, request: Any) -> tuple[User, ApiToken] | None:
        header = authentication.get_authorization_header(request).decode()
        if not header.startswith(f"{self.keyword} "):
            return None
        raw = header[len(self.keyword) + 1 :].strip()
        if not raw.startswith(ApiToken.PREFIX):
            return None

        try:
            token = ApiToken.objects.select_related("user").get(token_hash=ApiToken.hash_token(raw))
        except ApiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Token topilmadi") from None

        if token.revoked_at is not None:
            raise exceptions.AuthenticationFailed("Token bekor qilingan")
        if token.expires_at <= timezone.now():
            raise exceptions.AuthenticationFailed("Token muddati tugagan")
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("Foydalanuvchi faol emas")

        # last_used_at ni yangilaymiz, lekin har so'rovda yozmaymiz —
        # bir daqiqada bir marta yetarli.
        now = timezone.now()
        if token.last_used_at is None or (now - token.last_used_at).total_seconds() > 60:
            ApiToken.objects.filter(pk=token.pk).update(last_used_at=now)

        return token.user, token

    def authenticate_header(self, request: Any) -> str:
        return self.keyword
