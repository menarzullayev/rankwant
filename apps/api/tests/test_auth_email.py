"""Ro'yxatdan o'tishda pochta — majburiy va yagona.

Pochta parolni tiklashning yagona kanali bo'ladi, ya'ni u bo'lmasa
foydalanuvchini tiklab bo'lmaydi, takrorlansa esa tiklash havolasi
qaysi hisobniki ekani noaniq qoladi.
"""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User


def register(**over: str):
    body = {
        "username": "yangi",
        "email": "yangi@example.com",
        "password": "Parol!12345",
    }
    body.update(over)
    return APIClient().post(reverse("register"), body, format="json")


@pytest.mark.django_db
class TestEmailMajburiy:
    def test_emailsiz_qabul_qilinmaydi(self) -> None:
        r = APIClient().post(
            reverse("register"),
            {"username": "yangi", "password": "Parol!12345"},
            format="json",
        )

        assert r.status_code == 400
        assert "email" in str(r.data)
        assert not User.objects.filter(username="yangi").exists()

    def test_bosh_email_qabul_qilinmaydi(self) -> None:
        assert register(email="").status_code == 400

    def test_email_bilan_otadi(self) -> None:
        assert register().status_code == 201


@pytest.mark.django_db
class TestEmailYagona:
    def test_band_email(self, user) -> None:
        user.email = "aziz@example.com"
        user.save(update_fields=["email"])

        r = register(email="aziz@example.com")

        assert r.status_code == 400
        assert "band" in str(r.data)

    def test_registr_ahamiyatsiz(self, user) -> None:
        """`Aziz@` va `aziz@` pochta xizmati uchun bitta quti."""
        user.email = "aziz@example.com"
        user.save(update_fields=["email"])

        assert register(email="AZIZ@Example.COM").status_code == 400

    def test_bazada_ham_kafolat(self, user, other_user) -> None:
        """Serializer parallel so'rovda o'tkazib yuborishi mumkin."""
        user.email = "aziz@example.com"
        user.save(update_fields=["email"])

        with pytest.raises(IntegrityError), transaction.atomic():
            other_user.email = "Aziz@Example.com"
            other_user.save(update_fields=["email"])

    def test_bosh_email_takrorlanishi_mumkin(self, user, other_user) -> None:
        """Import qilingan mualliflar va stress foydalanuvchilarida pochta yo'q."""
        user.email = ""
        user.save(update_fields=["email"])
        other_user.email = ""
        other_user.save(update_fields=["email"])

        assert User.objects.filter(email="").count() == 2


@pytest.mark.django_db
class TestProfilTahriri:
    def test_bandini_yoza_olmaydi(self, user, other_user) -> None:
        other_user.email = "band@example.com"
        other_user.save(update_fields=["email"])
        c = APIClient()
        c.force_authenticate(user=user)

        r = c.patch(reverse("me"), {"email": "BAND@example.com"}, format="json")

        assert r.status_code == 400

    def test_ozinikini_qayta_yozishi_mumkin(self, user) -> None:
        user.email = "meniki@example.com"
        user.save(update_fields=["email"])
        c = APIClient()
        c.force_authenticate(user=user)

        r = c.patch(reverse("me"), {"email": "meniki@example.com"}, format="json")

        assert r.status_code == 200


@pytest.mark.django_db
class TestXatoMatni:
    def test_band_username_ozbekcha(self, user) -> None:
        """O'lchandi: DRF ning `UniqueValidator` i inglizcha matn qaytarardi."""
        r = register(username=user.username, email="boshqa@example.com")

        assert r.status_code == 400
        details = r.data["error"]["details"]
        assert details["username"] == ["Bu username band"]

    def test_band_email_ozbekcha(self, user) -> None:
        user.email = "aziz@example.com"
        user.save(update_fields=["email"])

        r = register(email="aziz@example.com")

        assert r.data["error"]["details"]["email"] == ["Bu email band"]
