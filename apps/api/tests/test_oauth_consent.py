"""OAuth roziligi va qaytish manzili — ikkalasi ham keyin qo'shildi.

Ikki mustaqil mavzu, lekin ikkalasi ham `SocialCallbackView._finish`
atrofida: birinchisi hisob ochilganda shartlar roziligini qayd etadi,
ikkinchisi kirgandan keyin odamni kutgan sahifasiga qaytaradi.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import oauth, views
from core.models import SocialAccount, User

BOT = "123456:AAbbCCddEEff"


@pytest.fixture
def sozlangan(settings: Any) -> Any:
    settings.GOOGLE_CLIENT_ID = "cid"
    settings.GOOGLE_CLIENT_SECRET = "secret"
    settings.TELEGRAM_BOT_TOKEN = BOT
    settings.TELEGRAM_BOT_USERNAME = "rankwant_bot"
    settings.SITE_URL = "https://rankwant.uz"
    return settings


def kelgan(monkeypatch: pytest.MonkeyPatch, email: str, uid: str = "u1") -> None:
    """Provayder API'siga chiqmasdan kimlikni soxtalashtiradi."""
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
        reverse("social-callback", args=["google"]) + f"?code=c&state={state}",
        follow=False,
    )


@pytest.mark.django_db
class TestRozilik:
    """`terms_accepted_at` ijtimoiy kirishda ham yozilishi kerak.

    Email bilan ro'yxatdan o'tishda uni `RegisterSerializer` yozadi.
    OAuth'da esa forma umuman yo'q edi — natijada Google/GitHub bilan
    ochilgan hisoblarda maydon NULL qolib ketardi, ya'ni rozilik qayd
    ETILMAGAN hisoblar paydo bo'lardi (huquqiy nomuvofiqlik).
    """

    def test_yangi_hisobda_rozilik_yoziladi(
        self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        kelgan(monkeypatch, "yangi@example.com")

        callback(APIClient())

        user = User.objects.get(email="yangi@example.com")
        assert user.terms_accepted_at is not None

    def test_mavjud_hisobda_rozilik_yoziladi(
        self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        user = User.objects.create_user(
            username="bor", email="bor@example.com", password="parol-12345"
        )
        assert user.terms_accepted_at is None
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        kelgan(monkeypatch, "bor@example.com")

        callback(APIClient())

        user.refresh_from_db()
        assert user.terms_accepted_at is not None

    def test_birinchi_sana_ustidan_yozilmaydi(
        self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Bu yerda BIRINCHI rozilik sanasi turadi — keyingi kirishlar
        uni yangilab yuborsa, sana hech narsani bildirmay qolardi."""
        oldin = timezone.now() - timedelta(days=30)
        user = User.objects.create_user(
            username="bor", email="bor@example.com", password="parol-12345"
        )
        user.terms_accepted_at = oldin
        user.save(update_fields=["terms_accepted_at"])
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        kelgan(monkeypatch, "bor@example.com")

        callback(APIClient())

        user.refresh_from_db()
        assert user.terms_accepted_at == oldin

    def test_yordamchi_bosh_maydonni_toldiradi(self, db: Any) -> None:
        user = User.objects.create_user(
            username="yalang", email="yalang@example.com", password="parol-12345"
        )

        views.record_social_consent(user)

        user.refresh_from_db()
        assert user.terms_accepted_at is not None


@pytest.mark.django_db
class TestQaytishManzili:
    """`?next=` — kirgandan keyin qaytish (qaror 1).

    Manzil ishonchsiz: uni har kim manzil qatorida tahrirlay oladi.
    Tekshirilmasa sayt OCHIQ REDIRECT beradigan bo'lardi — firibgar
    havola yuborib odamni boshqa saytga olib chiqishi mumkin edi.
    """

    @pytest.mark.parametrize(
        "qiymat",
        [
            "https://soxta.uz",  # mutlaq manzil
            "//soxta.uz",  # protokol-nisbiy
            "/\\soxta.uz",  # ba'zi brauzerlar buni ham tashqi deb o'qiydi
            "soxta",  # `/` bilan boshlanmaydi
            "",  # bo'sh
            None,  # umuman yo'q
        ],
    )
    def test_tashqi_manzil_rad_etiladi(self, qiymat: str | None) -> None:
        assert views.safe_next(qiymat) == ""

    @pytest.mark.parametrize(
        "qiymat",
        ["/settings/profil", "/masalalar/1?x=2", "/"],
    )
    def test_ichki_manzil_qabul_qilinadi(self, qiymat: str) -> None:
        assert views.safe_next(qiymat) == qiymat

    def test_start_next_ni_sessiyaga_yozadi(self, sozlangan: Any) -> None:
        c = APIClient()

        r = c.get(reverse("social-start", args=["google"]) + "?next=/settings/profil")

        assert r.status_code == 302
        assert c.session["social_next"] == "/settings/profil"

    def test_start_tashqi_manzilni_tashlaydi(self, sozlangan: Any) -> None:
        c = APIClient()

        c.get(reverse("social-start", args=["google"]) + "?next=https://soxta.uz")

        assert c.session["social_next"] == ""

    def test_oldingi_manzil_qolib_ketmaydi(self, sozlangan: Any) -> None:
        """Bo'sh qiymat ham YOZILADI: oldingi urinishdan qolgan manzil
        yangi kirishga «yopishib» qolmasligi kerak."""
        c = APIClient()
        c.get(reverse("social-start", args=["google"]) + "?next=/settings/profil")

        c.get(reverse("social-start", args=["google"]))

        assert c.session["social_next"] == ""

    def test_callback_qaytish_manziliga_yuboradi(
        self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        c = APIClient()
        c.get(reverse("social-start", args=["google"]) + "?next=/settings/profil")
        kelgan(monkeypatch, "yangi@example.com")

        r = callback(c)

        assert r["Location"] == "https://rankwant.uz/settings/profil"

    def test_manzilsiz_bosh_sahifaga(self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        kelgan(monkeypatch, "yangi@example.com")

        r = callback(APIClient())

        assert r["Location"] == "https://rankwant.uz/"

    def test_manzil_bir_marta_ishlatiladi(
        self, sozlangan: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sessiyadan O'CHIRIB olinadi: aks holda keyingi kirish ham
        eski manzilga tortib ketardi."""
        c = APIClient()
        c.get(reverse("social-start", args=["google"]) + "?next=/settings/profil")
        kelgan(monkeypatch, "birinchi@example.com")
        callback(c)

        assert c.session.get("social_next", "") == ""
