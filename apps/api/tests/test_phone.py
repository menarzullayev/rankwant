"""Telefon raqami — ixtiyoriy maydon (6-qaror).

Ikki narsa sinaladi: format tozalanadi, va raqam HECH QACHON ommaviy
profilga chiqmaydi. Ikkinchisi muhimroq — `hidden_fields` orqali
yashirish bu yerda ishlamaydi, chunki telefon umuman ommaviy
serializerga kirmaydi.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import PRIVACY_FIELDS, User


def kirgan(user: User) -> APIClient:
    """Haqiqiy sessiya bilan — `force_authenticate` sessiya ochmaydi."""
    client = APIClient()
    client.force_login(user)
    return client


def yoz(user: User, body: dict[str, Any]) -> Any:
    return kirgan(user).patch(reverse("me"), body, format="json")


@pytest.mark.django_db
class TestTelefonSaqlash:
    def test_saqlanadi(self, user: User) -> None:
        r = yoz(user, {"phone": "+998901234567"})

        assert r.status_code == 200
        user.refresh_from_db()
        assert user.phone == "+998901234567"

    @pytest.mark.parametrize(
        "kiritilgan",
        [
            "+998 90 123 45 67",
            "+998-90-123-45-67",
            "+998 (90) 1234567",
            "  +998901234567  ",
        ],
    )
    def test_format_tozalanadi(self, user: User, kiritilgan: str) -> None:
        """Bir xil raqam ikki xil ko'rinishda saqlansa, keyinchalik
        qidirish va solishtirish ishlamaydi."""
        yoz(user, {"phone": kiritilgan})

        user.refresh_from_db()
        assert user.phone == "+998901234567"

    def test_bosh_qiymat_ruxsat(self, user: User) -> None:
        """Maydon ixtiyoriy — bo'shatish ham mumkin."""
        r = yoz(user, {"phone": ""})

        assert r.status_code == 200
        user.refresh_from_db()
        assert user.phone == ""

    @pytest.mark.parametrize(
        "notogri",
        [
            "abc",
            "+998 90 123 45 6a",
            "12",
            "+9989012345678901234",
            "<script>alert(1)</script>",
        ],
    )
    def test_notogri_qiymat_rad_etiladi(self, user: User, notogri: str) -> None:
        r = yoz(user, {"phone": notogri})

        assert r.status_code == 400
        user.refresh_from_db()
        assert user.phone == ""

    def test_boshqa_maydonlar_tegilmaydi(self, user: User) -> None:
        """Telefon yuborilganda qolgan maydonlar bo'shab qolmasin."""
        user.country = "UZ"
        user.region = "samarqand"
        user.save(update_fields=["country", "region"])

        yoz(user, {"phone": "+998901234567"})

        user.refresh_from_db()
        assert user.country == "UZ"
        assert user.region == "samarqand"


@pytest.mark.django_db
class TestTelefonMaxfiyligi:
    """Telefon ommaviy profilga CHIQMAYDI.

    `PRIVACY_FIELDS` — foydalanuvchi yashira OLADIGAN maydonlar ro'yxati.
    Telefon u yerga kirmaydi, chunki u umuman ommaviy emas: yashirish
    tushunchasi yo'q. Ya'ni uni `hidden_fields` dan olib tashlash ham
    raqamni oshkor qilmasligi kerak.
    """

    def test_privacy_fields_ga_kirmaydi(self) -> None:
        assert "phone" not in PRIVACY_FIELDS

    def test_ommaviy_profilda_yoq(self, user: User) -> None:
        user.phone = "+998901234567"
        user.hidden_fields = []
        user.save(update_fields=["phone", "hidden_fields"])

        r = APIClient().get(reverse("user-detail", args=[user.username]))

        assert r.status_code == 200
        assert "phone" not in r.json()

    def test_oz_profilida_korinadi(self, user: User) -> None:
        """Egasi o'z raqamini ko'rishi kerak — sozlamalarda tahrirlaydi."""
        user.phone = "+998901234567"
        user.save(update_fields=["phone"])

        r = kirgan(user).get(reverse("me"))

        assert r.status_code == 200
        assert r.json()["phone"] == "+998901234567"
