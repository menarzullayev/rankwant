"""Ijtimoiy kirish — ADR-0016.

Provayder API'siga chiqilmaydi: `oauth.identity` soxtalashtiriladi va
faqat BIZNING mantiq sinaladi — hisob topish, yaratish va eng muhimi
bog'lash qoidasi.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core import oauth
from core.models import SocialAccount, User

BOT = "123456:AAbbCCddEEff"


@pytest.fixture
def sozlangan(settings: Any) -> Any:
    settings.GOOGLE_CLIENT_ID = "cid"
    settings.GOOGLE_CLIENT_SECRET = "secret"
    settings.TELEGRAM_BOT_TOKEN = BOT
    settings.TELEGRAM_BOT_USERNAME = "rankwant_bot"
    settings.SITE_URL = "https://rankwant.bugvector.uz"
    return settings


def kelgan(monkeypatch: pytest.MonkeyPatch, email: str, uid: str = "u1") -> None:
    monkeypatch.setattr(
        oauth,
        "identity",
        lambda provider, code: oauth.Identity(provider, uid, email, email.split("@")[0]),
    )


def callback(client: APIClient, state: str = "s1") -> Any:
    session = client.session
    session["social_state"] = state
    session.save()
    return client.get(
        reverse("social-callback", args=["google"]) + f"?code=c&state={state}", follow=False
    )


class TestSozlash:
    def test_kalitsiz_provayder_royxatda_yoq(self, settings: Any) -> None:
        settings.GOOGLE_CLIENT_ID = ""
        settings.GITHUB_CLIENT_ID = ""
        settings.TELEGRAM_BOT_TOKEN = ""

        assert oauth.configured() == []

    def test_kalitli_provayder_royxatda(self, sozlangan: Any) -> None:
        assert "google" in oauth.configured()
        assert "telegram" in oauth.configured()

    @pytest.mark.django_db
    def test_endpoint_royxatni_qaytaradi(self, sozlangan: Any) -> None:
        r = APIClient().get(reverse("auth-providers"))

        assert r.status_code == 200
        assert "google" in r.data["providers"]


@pytest.mark.django_db
class TestBoshlash:
    def test_provayderga_yonaltiradi(self, sozlangan: Any) -> None:
        r = APIClient().get(reverse("social-start", args=["google"]))

        assert r.status_code == 302
        assert str(r.headers["Location"]).startswith("https://accounts.google.com/")

    def test_kalitsiz_provayder_yonaltirmaydi(self, settings: Any) -> None:
        settings.GOOGLE_CLIENT_ID = ""

        r = APIClient().get(reverse("social-start", args=["google"]))

        assert "social=unavailable" in r.headers["Location"]


@pytest.mark.django_db
class TestCallback:
    def test_state_mos_kelmasa_rad_etiladi(self, sozlangan: Any) -> None:
        """CSRF: begona sayt bizning callback'imizga o'z kodini yubora olmaydi."""
        c = APIClient()
        session = c.session
        session["social_state"] = "haqiqiy"
        session.save()

        r = c.get(reverse("social-callback", args=["google"]) + "?code=c&state=soxta")

        assert "social=error" in r.headers["Location"]

    def test_statesiz_sorov_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """`None != None` yolg'on bo'lgani uchun, `state` siz kelgan so'rov
        ochiq oqimi yo'q brauzerda tekshiruvdan o'tib ketardi — hujumchi
        qurbonni o'z hisobiga kiritib qo'ya olardi (login CSRF)."""
        kelgan(monkeypatch, "hujumchi@example.com")

        r = APIClient().get(reverse("social-callback", args=["google"]) + "?code=c")

        assert "social=error" in r.headers["Location"]
        assert not User.objects.exists(), "hisob ochilmasin"

    def test_yangi_hisob_yaratiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        kelgan(monkeypatch, "yangi@example.com")
        c = APIClient()

        r = callback(c)

        assert r.status_code == 302
        user = User.objects.get(email="yangi@example.com")
        assert SocialAccount.objects.filter(user=user, provider="google").exists()
        assert not user.has_usable_password(), "parol o'rnatilmagan bo'lishi kerak"

    def test_provayder_pochtasi_tasdiqlangan_hisoblanadi(
        self, sozlangan: Any, monkeypatch: Any
    ) -> None:
        """`oauth` moduli Google'dan `email_verified` bo'lmasa manzilni
        UMUMAN olmaydi. Ya'ni manzil kelgan bo'lsa, uni bizdan kuchliroq
        tomon tekshirgan — ustidan yana o'z xatimizni yuborish keraksiz.
        O'lchandi: usiz Google bilan ochilgan hisobda «pochtangiz
        tasdiqlanmagan» banneri turardi."""
        kelgan(monkeypatch, "yangi@example.com")

        callback(APIClient())

        assert User.objects.get(email="yangi@example.com").email_verified_at is not None

    def test_boglangan_hisob_darhol_kiradi(self, sozlangan: Any, monkeypatch: Any) -> None:
        user = User.objects.create_user(username="bor", email="bor@example.com")
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        kelgan(monkeypatch, "boshqa@example.com")

        r = callback(APIClient())

        assert str(r.headers["Location"]).endswith("/")
        assert User.objects.count() == 1, "yangi hisob ochilmasin"


@pytest.mark.django_db
class TestBoglash:
    """ADR-0016 ning eng muhim qoidasi.

    Emailni tasdiqlash majburiy emas, ya'ni kimdir begona manzilni yozib
    hisob ochishi mumkin. Avtomatik bog'lash o'sha manzilning haqiqiy
    egasiga BEGONA hisobni ochib berardi.
    """

    def test_mavjud_email_avtomatik_boglanmaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        User.objects.create_user(username="egasi", email="bor@example.com", password="Parol!12345")
        kelgan(monkeypatch, "bor@example.com")

        r = callback(APIClient())

        assert "link=google" in r.headers["Location"]
        assert not SocialAccount.objects.exists(), "parolsiz bog'lanmasin"

    def test_togri_parol_boglaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        user = User.objects.create_user(
            username="egasi", email="bor@example.com", password="Parol!12345"
        )
        kelgan(monkeypatch, "bor@example.com")
        c = APIClient()
        callback(c)

        r = c.post(reverse("social-link"), {"password": "Parol!12345"}, format="json")

        user.refresh_from_db()
        assert r.status_code == 204
        assert SocialAccount.objects.filter(user=user, provider="google").exists()
        assert user.email_verified_at is not None, (
            "ikki isbot ham bor: provayder manzilni, foydalanuvchi parolni tasdiqladi"
        )

    def test_notogri_parol_boglamaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        User.objects.create_user(username="egasi", email="bor@example.com", password="Parol!12345")
        kelgan(monkeypatch, "bor@example.com")
        c = APIClient()
        callback(c)

        r = c.post(reverse("social-link"), {"password": "boshqa"}, format="json")

        assert r.status_code == 400
        assert not SocialAccount.objects.exists()

    def test_sorovsiz_boglab_bolmaydi(self, sozlangan: Any) -> None:
        User.objects.create_user(username="egasi", email="bor@example.com", password="Parol!12345")

        r = APIClient().post(reverse("social-link"), {"password": "Parol!12345"}, format="json")

        assert r.status_code == 400


class TestTelegram:
    def _imzo(self, payload: dict[str, str]) -> str:
        check = "\n".join(f"{k}={payload[k]}" for k in sorted(payload) if payload[k])
        secret = hashlib.sha256(BOT.encode()).digest()
        return hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()

    def test_togri_imzo_qabul_qilinadi(self, sozlangan: Any) -> None:
        payload = {"id": "77", "username": "ali", "auth_date": str(int(time.time()))}
        payload["hash"] = self._imzo(payload)

        ident = oauth.telegram_identity(payload)

        assert ident.uid == "77"
        assert ident.email == "", "Telegram pochta bermaydi"

    def test_soxta_imzo_rad_etiladi(self, sozlangan: Any) -> None:
        payload = {"id": "77", "auth_date": str(int(time.time())), "hash": "0" * 64}

        with pytest.raises(oauth.OAuthError):
            oauth.telegram_identity(payload)

    def test_eskirgan_imzo_rad_etiladi(self, sozlangan: Any) -> None:
        """Qayta yuborishning oldini oladi: eski imzolangan ma'lumot bilan
        kirib bo'lmaydi."""
        payload = {"id": "77", "auth_date": str(int(time.time()) - oauth.TELEGRAM_MAX_AGE - 60)}
        payload["hash"] = self._imzo(payload)

        with pytest.raises(oauth.OAuthError):
            oauth.telegram_identity(payload)


@pytest.mark.django_db
class TestTaxallusTanlash:
    def test_band_nom_raqam_oladi(self) -> None:
        User.objects.create_user(username="ali", email="a@example.com")

        assert oauth.free_username("ali") == "ali2"

    def test_qoidaga_mos_kelmagan_nom_tozalanadi(self) -> None:
        """Provayder bo'sh joyli yoki kirill nom berishi mumkin —
        chiziqcha esa endi ruxsat etilgan va saqlanadi."""
        nom = oauth.free_username("ali-valiyev jr")

        assert " " not in nom
        assert "-" in nom
        assert "лишний" not in oauth.free_username("алиlishniy")

    def test_taqlid_ham_hisobga_olinadi(self) -> None:
        """Yangi hisobga mavjud nomga o'xshash taxallus berilmasin."""
        User.objects.create_user(username="admin", email="a@example.com")

        assert oauth.free_username("аdmin") != "аdmin"
