"""Auth va PAT scope — ADR-0008. DoD: qamrov MAJBURIY."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import views
from core.models import ApiToken


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestRegistrationLogin:
    def test_royxatdan_otish(self, client: APIClient) -> None:
        r = client.post(
            reverse("register"), {"username": "yangi", "email": "y@a.uz", "password": "Parol!12345"}
        )
        assert r.status_code == 201

    def test_qisqa_parol_rad_etiladi(self, client: APIClient) -> None:
        r = client.post(reverse("register"), {"username": "x", "password": "123"})
        assert r.status_code == 400

    def test_login_va_me(self, client: APIClient, user) -> None:
        r = client.post(reverse("login"), {"username": "aziz", "password": "Parol!12345"})
        assert r.status_code == 200
        assert client.get(reverse("me")).status_code == 200

    def test_notogri_parol(self, client: APIClient, user) -> None:
        r = client.post(reverse("login"), {"username": "aziz", "password": "notogri"})
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "invalid_credentials"

    def test_anonim_me_ga_kira_olmaydi(self, client: APIClient) -> None:
        assert client.get(reverse("me")).status_code in (401, 403)


@pytest.mark.django_db
class TestApiToken:
    def test_ochiq_token_faqat_bir_marta(self, user) -> None:
        token, raw = ApiToken.issue(user, "ci", ["read"], timezone.now() + timedelta(days=30))
        assert raw.startswith("rw_")
        # Bazada faqat hash
        assert token.token_hash == ApiToken.hash_token(raw)
        assert raw not in str(ApiToken.objects.values().first())

    def test_bearer_bilan_kirish(self, client: APIClient, user) -> None:
        _, raw = ApiToken.issue(user, "ci", ["read"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 200

    def test_muddati_otgan_token(self, client: APIClient, user) -> None:
        _, raw = ApiToken.issue(user, "eski", ["read"], timezone.now() - timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 401

    def test_bekor_qilingan_token(self, client: APIClient, user) -> None:
        token, raw = ApiToken.issue(user, "x", ["read"], timezone.now() + timedelta(days=1))
        token.revoked_at = timezone.now()
        token.save()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 401

    def test_notogri_token(self, client: APIClient, user) -> None:
        client.credentials(HTTP_AUTHORIZATION="Bearer rw_qalbaki")
        assert client.get(reverse("me")).status_code == 401

    def test_read_scope_submit_qila_olmaydi(
        self, client: APIClient, user, problem, language
    ) -> None:
        """ADR-0008 minimal ruxsat: `read` token yechim yubora olmaydi."""
        _, raw = ApiToken.issue(user, "readonly", ["read"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        r = client.post(
            reverse("attempt-list"),
            {"problem": problem.slug, "language": language.code, "source_code": "int main(){}"},
        )
        assert r.status_code == 403

    def test_submit_scope_ishlaydi(self, client: APIClient, user, problem, language) -> None:
        _, raw = ApiToken.issue(user, "bot", ["read", "submit"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        r = client.post(
            reverse("attempt-list"),
            {"problem": problem.slug, "language": language.code, "source_code": "int main(){}"},
        )
        assert r.status_code == 201

    def test_token_limiti(self, client: APIClient, user) -> None:
        client.force_authenticate(user=user)
        expires = (timezone.now() + timedelta(days=30)).isoformat()
        for i in range(ApiToken.MAX_ACTIVE_PER_USER):
            ApiToken.issue(user, f"t{i}", ["read"], timezone.now() + timedelta(days=30))
        r = client.post(
            reverse("apitoken-list"),
            {"name": "ortiqcha", "scopes": ["read"], "expires_at": expires},
            format="json",
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "token_limit"

    def test_muddat_bir_yildan_oshmaydi(self, client: APIClient, user) -> None:
        client.force_authenticate(user=user)
        r = client.post(
            reverse("apitoken-list"),
            {
                "name": "uzoq",
                "scopes": ["read"],
                "expires_at": (timezone.now() + timedelta(days=400)).isoformat(),
            },
            format="json",
        )
        assert r.status_code == 400

    def test_ochirish_bekor_qiladi(self, client: APIClient, user) -> None:
        """Audit izi saqlanishi uchun o'chirilmaydi, bekor qilinadi."""
        token, _ = ApiToken.issue(user, "x", ["read"], timezone.now() + timedelta(days=1))
        client.force_authenticate(user=user)
        assert client.delete(reverse("apitoken-detail", args=[token.pk])).status_code == 204
        token.refresh_from_db()
        assert token.revoked_at is not None


@pytest.mark.django_db
class TestHealth:
    """Readiness bog'liqliklarni haqiqatan tekshirishi kerak.

    Avval endpoint shartsiz `ok` qaytarardi: chaos sinovi Postgres'ni
    o'chirganda ham 200 olardi, ya'ni hech narsa o'lchanmasdi.
    """

    def test_hammasi_ishlaganda_200(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_redis", lambda: "ok")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 200
        assert r.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}

    def test_redis_yiqilganda_503(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_redis", lambda: "ConnectionError")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"
        assert r.json()["checks"]["redis"] == "ConnectionError"

    def test_db_yiqilganda_503(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_database", lambda: "OperationalError")
        monkeypatch.setattr(views, "_check_redis", lambda: "ok")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 503
        assert r.json()["checks"]["database"] == "OperationalError"

    def test_health_throttle_kesh_ga_tayanmaydi(self) -> None:
        """Redis o'lganda throttle o'zi yiqilib, hisobotni bermay qo'yardi."""
        from core.views import HealthView

        assert HealthView.throttle_classes == []


@pytest.mark.django_db
class TestDependencyErrors:
    """Bog'liqlik uzilishi 500 emas, toza 503 bo'lishi kerak (10-operations)."""

    def test_redis_uzilishi_503(self) -> None:
        import redis as redis_lib

        from core.errors import exception_handler

        r = exception_handler(redis_lib.exceptions.ConnectionError("down"), {})
        assert r is not None
        assert r.status_code == 503
        assert r.data["error"]["code"] == "dependency_unavailable"

    def test_db_uzilishi_503(self) -> None:
        from django.db.utils import OperationalError

        from core.errors import exception_handler

        r = exception_handler(OperationalError("down"), {})
        assert r is not None
        assert r.status_code == 503


@pytest.mark.django_db
class TestPlatformStats:
    """Mehmon bosh sahifasi raqamlari — autentifikatsiyasiz ochiq."""

    def test_stats_ochiq_va_toliq(self, user, problem, contest) -> None:
        r = APIClient().get(reverse("platform-stats"))
        assert r.status_code == 200
        assert set(r.json()) == {
            "users",
            "problems",
            "contests",
            "attempts",
            "statement_locales",
        }
        assert r.json()["problems"] >= 1
        # Arxivdagi til filtri shu ro'yxatga qarab ko'rsatiladi.
        assert r.json()["statement_locales"] == ["uz"]

    def test_urinishlar_sanaladi(self, user, problem, language) -> None:
        from judging.models import Attempt

        cache.delete("platform-stats")
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        assert APIClient().get(reverse("platform-stats")).json()["attempts"] == 1
