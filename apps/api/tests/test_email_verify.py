"""Pochtani tasdiqlash — ADR-0016.

Tasdiqlash YUMSHOQ: u hech qanday eshikni yopmaydi, faqat manzil
ishlashini qayd etadi. Shu sababli asosiy tekshiruvlar «tasdiqlanmagan
odam ishlay oladimi» va «token qachon ishlamaydi» degan ikki savolga
qaratilgan.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import verification
from core.models import EmailVerifyToken, User


def register(client: APIClient, username: str = "yangi") -> Any:
    return client.post(
        reverse("register"),
        {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Parol!12345",
            # Rozilik MAJBURIY (qaror 13).
            "terms_accepted": True,
        },
        format="json",
    )


@pytest.fixture(autouse=True)
def navbat(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, ...]]:
    """Celery brokeri sinovda yo'q — chaqiruvlar ro'yxatga yig'iladi."""
    chaqiruvlar: list[tuple[Any, ...]] = []
    monkeypatch.setattr("core.views.send_email_verify.delay", lambda *a, **k: chaqiruvlar.append(a))
    return chaqiruvlar


@pytest.fixture
def odam(db: None) -> User:
    return User.objects.create_user(username="ali", email="ali@example.com", password="Parol!12345")


@pytest.mark.django_db
class TestRoyxatdanOtish:
    def test_token_chiqariladi(self, navbat: list[tuple[Any, ...]]) -> None:
        assert register(APIClient()).status_code == 201

        user = User.objects.get(username="yangi")
        assert EmailVerifyToken.objects.filter(user=user).count() == 1
        assert user.email_verified_at is None, "hali tasdiqlanmagan"
        assert navbat and navbat[0][0] == user.pk, "xat navbatga qo'yilishi kerak"

    def test_tasdiqlanmagan_odam_kira_oladi(self) -> None:
        """Yumshoq tasdiqlashning butun mazmuni shu: xat kelmasa ham
        platforma ishlaydi. Qattiq qilinsa xat yo'qolgan odam butunlay
        yo'qolardi."""
        client = APIClient()
        register(client)

        r = client.post(
            reverse("login"), {"identifier": "yangi", "password": "Parol!12345"}, format="json"
        )

        assert r.status_code == 200
        assert r.data["email_verified"] is False


@pytest.mark.django_db
class TestTasdiqlash:
    def test_togri_havola_tasdiqlaydi(self, odam: User) -> None:
        issued = verification.issue(odam)

        r = APIClient().post(reverse("email-verify"), {"token": issued.raw}, format="json")

        odam.refresh_from_db()
        assert r.status_code == 204
        assert odam.email_verified_at is not None

    def test_kod_bilan_ham_tasdiqlanadi(self, odam: User) -> None:
        """Havola telefondagi pochtadan kompyuterga o'tmaydi, kod esa
        o'tadi — parolni tiklashdagi bilan bir xil sabab."""
        issued = verification.issue(odam)

        r = APIClient().post(
            reverse("email-verify"),
            {"code": issued.code, "username": odam.username},
            format="json",
        )

        odam.refresh_from_db()
        assert r.status_code == 204
        assert odam.email_verified_at is not None

    def test_soxta_havola_rad_etiladi(self, odam: User) -> None:
        r = APIClient().post(reverse("email-verify"), {"token": "yoq"}, format="json")

        odam.refresh_from_db()
        assert r.status_code == 400
        assert odam.email_verified_at is None

    def test_ishlatilgan_havola_qayta_ishlamaydi(self, odam: User) -> None:
        issued = verification.issue(odam)
        APIClient().post(reverse("email-verify"), {"token": issued.raw}, format="json")

        r = APIClient().post(reverse("email-verify"), {"token": issued.raw}, format="json")

        assert r.status_code == 400

    def test_muddati_tugagan_havola_ishlamaydi(self, odam: User) -> None:
        issued = verification.issue(odam)
        EmailVerifyToken.objects.filter(pk=issued.row.pk).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        r = APIClient().post(reverse("email-verify"), {"token": issued.raw}, format="json")

        assert r.status_code == 400

    def test_manzil_almashsa_havola_kuchini_yoqotadi(self, odam: User) -> None:
        """Aks holda eski havola YANGI manzilni tasdiqlab yuborardi —
        holbuki u manzilga hech qanday xat bormagan."""
        issued = verification.issue(odam)
        odam.email = "boshqa@example.com"
        odam.save(update_fields=["email"])

        r = APIClient().post(reverse("email-verify"), {"token": issued.raw}, format="json")

        odam.refresh_from_db()
        assert r.status_code == 400
        assert odam.email_verified_at is None

    def test_yangi_token_eskisini_yopadi(self, odam: User) -> None:
        eski = verification.issue(odam)
        verification.issue(odam)

        r = APIClient().post(reverse("email-verify"), {"token": eski.raw}, format="json")

        assert r.status_code == 400, "pochtada ikkita amaldagi havola qolmasin"


@pytest.mark.django_db
class TestQaytaYuborish:
    def test_kirmagan_odam_yubora_olmaydi(self) -> None:
        assert APIClient().post(reverse("email-verify-resend")).status_code in (401, 403)

    def test_kirgan_odam_yangi_token_oladi(self, odam: User) -> None:
        client = APIClient()
        client.force_authenticate(odam)

        assert client.post(reverse("email-verify-resend")).status_code == 204
        assert EmailVerifyToken.objects.filter(user=odam).count() == 1

    def test_tasdiqlangan_odamga_yuborilmaydi(self, odam: User) -> None:
        odam.email_verified_at = timezone.now()
        odam.save(update_fields=["email_verified_at"])
        client = APIClient()
        client.force_authenticate(odam)

        assert client.post(reverse("email-verify-resend")).status_code == 204
        assert not EmailVerifyToken.objects.filter(user=odam).exists()

    def test_chegara_ishlaydi(self, odam: User) -> None:
        for _ in range(EmailVerifyToken.PER_USER_HOUR):
            verification.issue(odam)

        with pytest.raises(verification.TooManyRequests):
            verification.issue(odam)
