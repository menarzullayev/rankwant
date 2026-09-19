"""Ijtimoiy kirish — ADR-0016.

Provayder API'siga chiqilmaydi: `oauth.identity` soxtalashtiriladi va
faqat BIZNING mantiq sinaladi — hisob topish, yaratish va eng muhimi
bog'lash qoidasi.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core import account, oauth
from core.models import SocialAccount, User

#: Telegram OIDC credential'lari. Ataylab SOXTA: haqiqiy Client ID ham,
#: Secret ham repoga tushmasligi kerak (`.env.public` da yashaydi).
TG_CLIENT_ID = "123456789"
TG_CLIENT_SECRET = "be_test_secret"


@pytest.fixture
def sozlangan(settings: Any) -> Any:
    settings.GOOGLE_CLIENT_ID = "cid"
    settings.GOOGLE_CLIENT_SECRET = "secret"
    settings.TELEGRAM_CLIENT_ID = TG_CLIENT_ID
    settings.TELEGRAM_CLIENT_SECRET = TG_CLIENT_SECRET
    settings.SITE_URL = "https://rankwant.uz"
    return settings


def kelgan(monkeypatch: pytest.MonkeyPatch, email: str, uid: str = "u1") -> None:
    """Kimlikni soxtalashtiradi — provayder API'siga chiqilmaydi.

    Uchinchi argument (PKCE verifier) shart: callback uni har doim
    uzatadi, provayder esa ishlatmasa ham qabul qilishi kerak.
    """
    monkeypatch.setattr(
        oauth,
        "identity",
        lambda provider, code, verifier="": oauth.Identity(
            provider, uid, email, email.split("@")[0]
        ),
    )


def callback(client: APIClient, state: str = "s1") -> Any:
    session = client.session
    session["social_state"] = state
    session.save()
    return client.get(
        reverse("social-callback", args=["google"]) + f"?code=c&state={state}", follow=False
    )


def id_token(**claims: Any) -> str:
    """Imzosiz JWT qaytaradi.

    Imzo ATAYLAB tekshirilmaydi (OIDC Core 3.1.3.7, 6-qadam — token
    endpoint'idan to'g'ridan-to'g'ri kelgan `id_token` uchun TLS yetarli),
    shuning uchun testda ham imzo kerak emas: faqat tuzilish muhim.
    """
    base: dict[str, Any] = {
        "iss": oauth.TELEGRAM_ISSUER,
        "aud": TG_CLIENT_ID,
        "sub": "77",
        "preferred_username": "ali",
        "exp": int(time.time()) + 60,
    }
    base.update(claims)

    def part(obj: dict[str, Any]) -> str:
        raw = json.dumps(obj, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    return f"{part({'alg': 'RS256', 'typ': 'JWT'})}.{part(base)}.imzo"


def almashuv(monkeypatch: pytest.MonkeyPatch, token: str) -> None:
    """`/token` javobini soxtalashtiradi — tarmoqqa chiqilmaydi."""
    monkeypatch.setattr(oauth, "_request", lambda *a, **k: {"id_token": token})


class TestSozlash:
    def test_kalitsiz_provayder_royxatda_yoq(self, settings: Any) -> None:
        settings.GOOGLE_CLIENT_ID = ""
        settings.GITHUB_CLIENT_ID = ""
        settings.TELEGRAM_CLIENT_ID = ""

        assert oauth.configured() == []

    def test_kalitli_provayder_royxatda(self, sozlangan: Any) -> None:
        assert "google" in oauth.configured()
        assert "telegram" in oauth.configured()

    @pytest.mark.django_db
    def test_endpoint_royxatni_qaytaradi(self, sozlangan: Any) -> None:
        from django.core.cache import cache

        cache.delete("auth-providers")
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
    """OIDC: kod token'ga almashadi, kimlik `id_token` ichidan o'qiladi."""

    def test_sub_va_taxallus_olinadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token())

        ident = oauth.identity("telegram", "kod", "verifier")

        assert ident.provider == "telegram"
        assert ident.uid == "77"
        assert ident.handle == "ali"
        assert ident.email == "", "Telegram pochta bermaydi"

    def test_taxallus_bosh_bolsa_uid_dan_yasaladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token(preferred_username=""))

        ident = oauth.identity("telegram", "kod", "verifier")

        assert ident.suggested == "tg77"

    def test_boshqa_issuer_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token(iss="https://soxta.example"))

        with pytest.raises(oauth.OAuthError, match="iss"):
            oauth.identity("telegram", "kod", "verifier")

    def test_boshqa_audience_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """Boshqa bot uchun berilgan token bizning hisob ochmasligi kerak."""
        almashuv(monkeypatch, id_token(aud="999"))

        with pytest.raises(oauth.OAuthError, match="aud"):
            oauth.identity("telegram", "kod", "verifier")

    def test_aud_royxat_bolsa_ham_qabul_qilinadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token(aud=[TG_CLIENT_ID, "999"]))

        assert oauth.identity("telegram", "kod", "verifier").uid == "77"

    def test_muddati_tugagan_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token(exp=int(time.time()) - 1))

        with pytest.raises(oauth.OAuthError, match="expired"):
            oauth.identity("telegram", "kod", "verifier")

    def test_sub_siz_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token(sub=""))

        with pytest.raises(oauth.OAuthError, match="sub"):
            oauth.identity("telegram", "kod", "verifier")

    def test_buzuq_token_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, "bu.jwt.emas")

        with pytest.raises(oauth.OAuthError):
            oauth.identity("telegram", "kod", "verifier")

    def test_id_token_yoq_bolsa_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        monkeypatch.setattr(oauth, "_request", lambda *a, **k: {})

        with pytest.raises(oauth.OAuthError):
            oauth.identity("telegram", "kod", "verifier")

    def test_pkce_challenge_s256(self) -> None:
        """`code_challenge` — base64url(SHA256(verifier)), to'ldirishsiz."""
        verifier, challenge = oauth.pkce_pair()
        kutilgan = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
            .rstrip(b"=")
            .decode("ascii")
        )

        assert challenge == kutilgan
        assert "=" not in challenge, "PKCE to'ldirishsiz bo'lishi shart"


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


@pytest.mark.django_db
class TestSozlamalardanBoglash:
    """Kirgan holda ulash — ADR-0016 dagi bo'shliq.

    Ilgari bog'lashni FAQAT kirish paytida boshlash mumkin edi va u
    provayder pochtasi hisob pochtasiga mos kelishini talab qilardi.
    O'lchangan oqibat: ish pochtasi bilan Google'ga kirgan odam o'z
    hisobiga ulanish o'rniga yangi hisob ochib olardi.
    """

    def start(self, client: APIClient, user: User | None = None) -> str:
        if user is not None:
            client.force_login(user)
        client.get(reverse("social-start", args=["google"]))
        return str(client.session["social_state"])

    def qaytish(self, client: APIClient, state: str) -> Any:
        return client.get(reverse("social-callback", args=["google"]) + f"?code=c&state={state}")

    def test_kirgan_odam_hisobiga_ulanadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        user = User.objects.create_user(
            username="egasi", email="uy@example.com", password="Parol!12345"
        )
        kelgan(monkeypatch, "ish@example.com")
        c = APIClient()
        state = self.start(c, user)

        r = self.qaytish(c, state)

        assert "social=linked" in r.headers["Location"]
        assert SocialAccount.objects.filter(user=user, provider="google").exists()
        assert User.objects.count() == 1, "yangi hisob ochilmasin"

    def test_pochta_mos_kelmasa_ham_ulanadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """Bog'lashning butun mazmuni shu: odam allaqachon o'zini
        isbotlagan, ya'ni pochta mosligiga tayanish keraksiz."""
        user = User.objects.create_user(
            username="egasi", email="uy@example.com", password="Parol!12345"
        )
        kelgan(monkeypatch, "butunlay@boshqa.com")
        c = APIClient()

        self.qaytish(c, self.start(c, user))

        assert (
            SocialAccount.objects.get(user=user, provider="google").email == "butunlay@boshqa.com"
        )

    def test_boshqa_hisobdagi_provayder_ulanmaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        birinchi = User.objects.create_user(username="bir", email="a@example.com")
        SocialAccount.objects.create(user=birinchi, provider="google", uid="u1")
        ikkinchi = User.objects.create_user(
            username="ikki", email="b@example.com", password="Parol!12345"
        )
        kelgan(monkeypatch, "c@example.com")
        c = APIClient()

        r = self.qaytish(c, self.start(c, ikkinchi))

        assert "social=taken" in r.headers["Location"]
        assert not SocialAccount.objects.filter(user=ikkinchi).exists()

    def test_kirmagan_odam_uchun_oqim_ozgarmaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        kelgan(monkeypatch, "yangi@example.com")
        c = APIClient()

        r = self.qaytish(c, self.start(c))

        assert "social=linked" not in r.headers["Location"]
        assert User.objects.filter(email="yangi@example.com").exists(), "hisob ochilishi kerak"


@pytest.mark.django_db
class TestUzish:
    def test_uziladi(self, sozlangan: Any) -> None:
        user = User.objects.create_user(
            username="egasi", email="a@example.com", password="Parol!12345"
        )
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        c = APIClient()
        c.force_login(user)

        r = c.delete(reverse("social-unlink", args=["google"]))

        assert r.status_code == 204
        assert not SocialAccount.objects.filter(user=user).exists()

    def test_yagona_kirish_yoli_uzilmaydi(self, sozlangan: Any) -> None:
        """Paroli yo'q va boshqa provayderi ham qolmagan odam hisobiga
        qaytib kira olmasdi."""
        user = User.objects.create_user(username="faqatgoogle", email="a@example.com")
        user.set_unusable_password()
        user.save(update_fields=["password"])
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        c = APIClient()
        c.force_login(user)

        r = c.delete(reverse("social-unlink", args=["google"]))

        assert r.status_code == 400
        assert SocialAccount.objects.filter(user=user).exists()

    def test_ikkinchi_provayder_qolsa_uziladi(self, sozlangan: Any) -> None:
        user = User.objects.create_user(username="ikkovi", email="a@example.com")
        user.set_unusable_password()
        user.save(update_fields=["password"])
        SocialAccount.objects.create(user=user, provider="google", uid="u1")
        SocialAccount.objects.create(user=user, provider="github", uid="u2")
        c = APIClient()
        c.force_login(user)

        assert c.delete(reverse("social-unlink", args=["google"])).status_code == 204

    def test_me_ulangan_royxatni_qaytaradi(self, sozlangan: Any) -> None:
        user = User.objects.create_user(
            username="egasi", email="a@example.com", password="Parol!12345"
        )
        SocialAccount.objects.create(user=user, provider="github", uid="u2")
        c = APIClient()
        c.force_login(user)

        assert c.get(reverse("me")).data["social"] == ["github"]


@pytest.mark.django_db
class TestTelegramniUlash:
    """Telegram ham endi `SocialStartView` dan o'tadi, ya'ni `state` va
    niyat qoidalari Google/GitHub bilan AYNAN bir xil.

    Ilgari u iframe vidjeti edi: callback'i `state` siz GET bo'lgani
    uchun «kirgan bo'lsa bog'la» qoidasi hisobni egallash yo'li bo'lardi.
    Shu sababli niyat alohida POST (`link-start`) bilan qo'yilardi —
    o'sha yo'l ham, o'sha sinov ham endi keraksiz.
    """

    def qaytish(self, client: APIClient, state: str = "s1") -> Any:
        session = client.session
        session["social_state"] = state
        session.save()
        return client.get(
            reverse("social-callback", args=["telegram"]) + f"?code=c&state={state}",
            follow=False,
        )

    def test_niyat_belgilangach_ulanadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        almashuv(monkeypatch, id_token())
        user = User.objects.create_user(
            username="egasi", email="a@example.com", password="Parol!12345"
        )
        c = APIClient()
        c.force_login(user)

        c.get(reverse("social-start", args=["telegram"]))  # niyat sessiyada
        r = self.qaytish(c)

        assert "social=linked" in r.headers["Location"]
        assert SocialAccount.objects.filter(user=user, provider="telegram", uid="77").exists()

    def test_niyatsiz_ulanmaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """Hujum shakli: hujumchi qurbonning brauzerini o'zining kodi bilan
        callback'ga yuboradi. Niyat sessiyada bo'lmagani uchun bu HECH
        QACHON bog'lanishga aylanmasligi kerak."""
        almashuv(monkeypatch, id_token())
        qurbon = User.objects.create_user(
            username="qurbon", email="a@example.com", password="Parol!12345"
        )
        c = APIClient()
        c.force_login(qurbon)

        self.qaytish(c)

        assert not SocialAccount.objects.filter(user=qurbon).exists(), "hisob egallanmasin"

    def test_state_siz_rad_etiladi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """`state` siz kelgan callback login CSRF bo'lardi (ADR-0016)."""
        almashuv(monkeypatch, id_token())
        c = APIClient()

        r = c.get(reverse("social-callback", args=["telegram"]) + "?code=c")

        assert "social=error" in r.headers["Location"]

    def test_boshqa_provayder_niyati_yetmaydi(self, sozlangan: Any, monkeypatch: Any) -> None:
        """Tashlab ketilgan Google urinishi keyinroq Telegram uchun eshik
        ochib qo'ymasligi kerak — shuning uchun niyat provayderga
        bog'langan."""
        almashuv(monkeypatch, id_token())
        user = User.objects.create_user(
            username="egasi", email="a@example.com", password="Parol!12345"
        )
        c = APIClient()
        c.force_login(user)
        c.get(reverse("social-start", args=["google"]))

        self.qaytish(c)

        assert not SocialAccount.objects.filter(user=user, provider="telegram").exists()


@pytest.mark.django_db
class TestOchirilganVaBloklangan:
    def test_ochirilgan_hisobning_eski_boglanishi_xalaqit_bermaydi(
        self, sozlangan: Any, monkeypatch: Any
    ) -> None:
        """Hisob o'chirilishidan OLDIN qolib ketgan bog'lanish: egasi o'sha
        Google bilan qaytsa yangi hisob ochilishi kerak, `uniq_social_uid`
        esa band turardi."""
        eski = User.objects.create_user(username="eski", email="e@example.com")
        SocialAccount.objects.create(user=eski, provider="google", uid="u1", email="e@example.com")
        eski.username = account.anonymous_name(eski)
        eski.email = ""
        eski.is_active = False
        eski.save()
        kelgan(monkeypatch, "e@example.com")

        r = callback(APIClient())

        assert r.status_code == 302
        yangi = SocialAccount.objects.get(provider="google", uid="u1").user
        assert yangi.pk != eski.pk
        assert yangi.is_active

    def test_bloklangan_hisobga_provayder_orqali_kirilmaydi(
        self, sozlangan: Any, monkeypatch: Any
    ) -> None:
        odam = User.objects.create_user(username="blok", email="b@example.com")
        SocialAccount.objects.create(user=odam, provider="google", uid="u1", email="b@example.com")
        odam.is_active = False
        odam.save(update_fields=["is_active"])
        kelgan(monkeypatch, "b@example.com")

        r = callback(APIClient())

        assert "social=error" in str(r.headers["Location"])
        assert SocialAccount.objects.get(provider="google", uid="u1").user == odam

    def test_provayder_rasmi_saqlanadi(self, sozlangan: Any, monkeypatch: Any) -> None:
        rasm = "https://lh3.googleusercontent.com/a/x=s96-c"
        monkeypatch.setattr(
            oauth,
            "identity",
            lambda provider, code, verifier="": oauth.Identity(
                provider, "u9", "r@example.com", "r", rasm
            ),
        )

        callback(APIClient())

        assert SocialAccount.objects.get(uid="u9").picture == rasm
