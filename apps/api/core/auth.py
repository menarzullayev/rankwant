"""Autentifikatsiya — PAT (ADR-0008) va kirish backend'i (4-qaror)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
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


class EmailOrUsernameBackend(ModelBackend):
    """`username` maydonida foydalanuvchi nomi YOKI email (4-qaror).

    Django'ning standart `ModelBackend` i `USERNAME_FIELD` (bizda
    `username`) bo'yicha qidiradi, ya'ni email kiritilganda hisob
    topilmasdi. Backend'ni almashtirish `django_authenticate(...)` ni
    chaqiruvchi HAMMA joyda ishlaydi — `LoginView` ham, admin panel ham.

    Ikkala ustun bir so'rovda qidiriladi (`OR`), ya'ni ikki marta
    pochtaga chiqish yo'q. Tartib muhim emas: `username` bazada
    yagonalashtirilgan (registrsiz) va email `uniq_email_ci` bilan
    cheklangan, ya'ni ikkalasi bir vaqtda mos kelsa ham natija bitta.

    `Q(email__iexact=...)` ATaylab: pochta xizmatlari uchun `Aziz@` va
    `aziz@` bitta quti, ya'ni registr farqi kutilmagan «topilmadi»
    berardi. Nom uchun ham `username__iexact` — bazadagi cheklov
    (`uniq_username_ci`) aynan shuni kafolatlaydi.
    """

    def authenticate(
        self,
        request: Any,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        value = username.strip()
        if not value:
            return None

        user = self._lookup(value)
        if user is None:
            # Parol xeshlashni BARIBIR bajaramiz: aks holda mavjud va
            # mavjud bo'lmagan hisob javob vaqti bo'yicha farqlanardi va
            # bu mavjud nomlarni sanab chiqish yo'li bo'lardi
            # (ADR-0015 — enumeratsiyaga qarshi).
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    @staticmethod
    def _lookup(value: str) -> User | None:
        """Nom yoki pochta bo'yicha bitta hisob.

        `MultipleObjectsReturned` — bir xil qiymat bir hisobning nomi,
        boshqasining pochtasi bo'lganda. Bunday holatda NOM ustun: u
        yagonaligi bazada kafolatlangan (`uniq_username_ci`), pochta esa
        tarixan takrorlanishi mumkin bo'lgan ustun.
        """
        try:
            return User.objects.get(Q(username__iexact=value) | Q(email__iexact=value))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return (
                User.objects.filter(username__iexact=value).first()
                or User.objects.filter(email__iexact=value).first()
            )
