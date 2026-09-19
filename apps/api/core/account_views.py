"""Hisob sozlamalari: parol, pochta, taxallus, sessiyalar, avatar.

`core/views.py` dan alohida: u yerda kirish oqimi yashaydi, bu yerda esa
kirgan odamning o'z hisobini boshqarishi.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_safe
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import exceptions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core import avatars, sessions, usernames, verification
from core.middleware import EDGE_CACHE_FLAG
from core.models import EmailVerifyToken, SocialAccount, User, UserSession
from core.serializers import (
    AvatarImportSerializer,
    EmailChangeSerializer,
    MeSerializer,
    PasswordChangeSerializer,
    UsernameChangeSerializer,
    UserSessionSerializer,
    _email_taken,
)
from core.tasks import queue, send_email_verify
from core.throttling import ResilientScopedRateThrottle


def _me(request: Request) -> User:
    assert isinstance(request.user, User)
    return request.user


@extend_schema(summary="Parolni o'zgartirish")
class PasswordChangeView(APIView):
    """Parolni almashtirish — yoki ijtimoiy hisobda birinchi marta o'rnatish.

    Paroli yo'q odam (faqat Google/GitHub/Telegram bilan kirgan) uchun
    joriy parol so'ralmaydi: u yo'q. Aks holda «yagona kirish yo'lini uzib
    bo'lmaydi — avval parol o'rnating» xabari bajarib bo'lmaydigan ishni
    buyurardi.

    Boshqa barcha sessiyalar uziladi: parol almashtirishning eng keng
    sababi — kimdir hisobga kirib olgani.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "account_change"

    @extend_schema(request=PasswordChangeSerializer, responses={204: None})
    def post(self, request: Request) -> Response:
        user = _me(request)
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if user.has_usable_password() and not user.check_password(data.get("old_password", "")):
            raise exceptions.ValidationError({"old_password": "Current password is wrong"})
        try:
            validate_password(data["new_password"], user)
        except DjangoValidationError as exc:
            raise exceptions.ValidationError({"new_password": exc.messages}) from None
        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        sessions.terminate_others(user, keep=request.session.session_key)
        # Joriy sessiya parol xeshiga bog'langan — yangilanmasa, odam
        # parolni almashtirgan zahoti o'zi ham tizimdan chiqib ketardi.
        update_session_auth_hash(request, user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="Email o'zgartirish (kod tasdiqlash bilan)")
class EmailChangeView(APIView):
    """Yangi manzilga kod yuboradi. `User.email` tasdiqlangunga qadar o'zgarmaydi.

    Tasdiqlash oddiy `auth/email/verify/` orqali: token maqsadini o'zi biladi.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "account_change"

    @extend_schema(request=EmailChangeSerializer, responses={202: None})
    def post(self, request: Request) -> Response:
        user = _me(request)
        serializer = EmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        if email.lower() == user.email.lower():
            raise exceptions.ValidationError({"email": "This is already your address"})
        if _email_taken(email, exclude=user):
            raise exceptions.ValidationError({"email": "This email is taken"})
        if user.has_usable_password() and not user.check_password(
            serializer.validated_data.get("password", "")
        ):
            raise exceptions.ValidationError({"password": "Password is wrong"})
        try:
            issued = verification.issue(user, email=email, purpose=EmailVerifyToken.Purpose.CHANGE)
        except verification.TooManyRequests as exc:
            raise exceptions.Throttled(detail="Too many requests — try again shortly") from exc
        queue(send_email_verify, user.pk, issued.raw, issued.code, email)
        return Response({"email": email}, status=status.HTTP_202_ACCEPTED)


class UsernameChangeView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "account_change"

    @extend_schema(
        summary="Username'ni o'zgartirish",
        request=UsernameChangeSerializer,
        responses={200: MeSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = UsernameChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            changed = usernames.change(
                _me(request),
                serializer.validated_data["username"],
                pay=serializer.validated_data["pay"],
            )
        except usernames.ChangeError as exc:
            details: dict[str, Any] = {"username": [str(exc)]}
            if exc.price is not None:
                details["price"] = exc.price
            return Response(
                {"error": {"code": exc.code, "message": str(exc), "details": details}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(MeSerializer(changed, context={"request": request}).data)


@extend_schema_view(
    get=extend_schema(summary="Kirilgan qurilmalar"),
    delete=extend_schema(summary="Boshqa sessiyalarni yopish"),
)
class SessionListView(APIView):
    """Kirilgan qurilmalar. `DELETE` — joriydan boshqa hammasini yopadi."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSessionSerializer(many=True)})
    def get(self, request: Request) -> Response:
        # Joriy sessiya ro'yxatda albatta bo'lsin — kuzatuv hali uni
        # yozmagan bo'lishi mumkin (u javobdan KEYIN ishlaydi).
        sessions.record(request, force=True)
        rows = sessions.live(_me(request))
        context = {"current_key": request.session.session_key}
        return Response(UserSessionSerializer(rows, many=True, context=context).data)

    @extend_schema(responses={204: None}, operation_id="me_sessions_terminate_others")
    def delete(self, request: Request) -> Response:
        sessions.terminate_others(_me(request), keep=request.session.session_key)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Sessiyani yopish", responses={204: None})
    def delete(self, request: Request, pk: int) -> Response:
        row = UserSession.objects.filter(user=_me(request), pk=pk).first()
        if row is None:
            raise exceptions.NotFound()
        current = row.session_key == request.session.session_key
        sessions.terminate(row)
        if current:
            logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


def _store_avatar(user: User, data: bytes) -> Response:
    try:
        name = avatars.put(data)
    except avatars.AvatarError as exc:
        raise exceptions.ValidationError({"file": str(exc)}) from None
    old = avatars.name_from_url(user.avatar_url)
    user.avatar_url = avatars.url_for(name)
    user.save(update_fields=["avatar_url"])
    if old:
        avatars.delete(old)
    from qvant.quests import on_profile_completed, profile_is_complete

    if profile_is_complete(user):
        on_profile_completed(user)
    return Response({"avatar_url": user.avatar_url})


@extend_schema_view(
    post=extend_schema(summary="Avatar yuklash"),
    delete=extend_schema(summary="Avatarni o'chirish"),
)
class AvatarView(APIView):
    """Rasm yuklash. Brauzer uni oldindan 256 pikselga kichraytiradi."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "avatar"

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
        responses={200: None},
    )
    def post(self, request: Request) -> Response:
        upload = request.FILES.get("file")
        if upload is None:
            raise exceptions.ValidationError({"file": "No file was sent"})
        if (upload.size or 0) > avatars.MAX_BYTES:
            raise exceptions.ValidationError({"file": "The image must not exceed 1 MB"})
        return _store_avatar(_me(request), upload.read(avatars.MAX_BYTES + 1))

    @extend_schema(responses={204: None})
    def delete(self, request: Request) -> Response:
        user = _me(request)
        old = avatars.name_from_url(user.avatar_url)
        user.avatar_url = ""
        user.save(update_fields=["avatar_url"])
        if old:
            avatars.delete(old)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="OAuth rasmini avatar qilish")
class AvatarImportView(APIView):
    """Ulangan Google/GitHub/Telegram hisobining rasmini avatar qiladi."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "avatar"

    @extend_schema(request=AvatarImportSerializer, responses={200: None})
    def post(self, request: Request) -> Response:
        user = _me(request)
        serializer = AvatarImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = SocialAccount.objects.filter(
            user=user, provider=serializer.validated_data["provider"]
        ).first()
        if account is None:
            raise exceptions.ValidationError({"provider": "This account is not linked"})
        url = avatars.provider_picture(account)
        if not url:
            raise exceptions.ValidationError(
                {"provider": "The provider did not return a photo — reconnect the account"}
            )
        try:
            data = avatars.fetch_remote(url)
        except avatars.AvatarError as exc:
            raise exceptions.ValidationError({"provider": str(exc)}) from None
        return _store_avatar(user, data)


@require_safe
def avatar_file(request: HttpRequest, name: str) -> HttpResponse:
    """Avatar faylini beradi.

    Oddiy Django view, DRF emas: rasm uchun kontent muzokarasi ham,
    sessiya ham, throttle ham kerak emas — leaderboard sahifasining o'zi
    o'nlab avatar so'raydi. Nom o'zgarmas, ya'ni javob abadiy keshlanadi.
    """
    found = avatars.get(name)
    if found is None:
        return HttpResponse(status=404)
    data, content_type = found
    response = HttpResponse(data, content_type=content_type)
    response["Cache-Control"] = "public, max-age=31536000, immutable"
    response["X-Content-Type-Options"] = "nosniff"
    setattr(response, EDGE_CACHE_FLAG, True)
    return response
