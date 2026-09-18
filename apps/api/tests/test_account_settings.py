"""Hisob sozlamalari — parol, pochta, taxallus, sessiyalar, avatar va profil maydonlari.

Har bo'limda asosiy savol «nima o'zgarmasligi kerak»: pochta tasdiqlanmaguncha,
taxallus pulsiz ikkinchi marta, sessiya esa egasidan boshqa hech kim tomonidan.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import avatars, usernames
from core.models import SocialAccount, User, UsernameHistory, UserSession
from qvant import ledger
from qvant.models import QvantTransaction

PAROL = "Parol!12345"
YANGI_PAROL = "Yangi!Parol789"
PNG = b"\x89PNG\r\n\x1a\n" + bytes(64)


def _yigish(chaqiruvlar: list[tuple[Any, ...]], name: str) -> Any:
    def delay(*args: Any) -> None:
        chaqiruvlar.append((name, *args))

    return delay


@pytest.fixture(autouse=True)
def navbat(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, ...]]:
    """Broker sinovda yo'q — xatlar ro'yxatga yig'iladi."""
    chaqiruvlar: list[tuple[Any, ...]] = []
    for name in ("send_email_verify", "send_email_changed"):
        monkeypatch.setattr(f"core.tasks.{name}.delay", _yigish(chaqiruvlar, name))
    return chaqiruvlar


def kirgan(user: User) -> APIClient:
    """Haqiqiy sessiya bilan — `force_authenticate` sessiya ochmaydi."""
    client = APIClient()
    client.force_login(user)
    return client


def chiqarilgan(client: APIClient) -> bool:
    return client.get(reverse("me")).status_code in (401, 403)


@pytest.mark.django_db
class TestParol:
    def test_almashtiriladi_va_joriy_sessiya_qoladi(self, user: User) -> None:
        c = kirgan(user)

        r = c.post(
            reverse("me-password"),
            {"old_password": PAROL, "new_password": YANGI_PAROL},
            format="json",
        )

        assert r.status_code == 204
        user.refresh_from_db()
        assert user.check_password(YANGI_PAROL)
        assert not chiqarilgan(c), "parolni almashtirgan odamning o'zi chiqib ketmasin"

    def test_joriy_parol_notogri_bolsa_rad(self, user: User) -> None:
        r = kirgan(user).post(
            reverse("me-password"),
            {"old_password": "xato", "new_password": YANGI_PAROL},
            format="json",
        )

        assert r.status_code == 400
        user.refresh_from_db()
        assert user.check_password(PAROL)

    def test_zaif_parol_rad(self, user: User) -> None:
        r = kirgan(user).post(
            reverse("me-password"), {"old_password": PAROL, "new_password": "123"}, format="json"
        )

        assert r.status_code == 400

    def test_parolsiz_hisobga_joriy_parol_soralmaydi(self, user: User) -> None:
        """Faqat Google/GitHub/Telegram bilan kirgan odamda joriy parol yo'q."""
        user.set_unusable_password()
        user.save(update_fields=["password"])
        c = kirgan(user)
        assert c.get(reverse("me")).data["has_password"] is False

        r = c.post(reverse("me-password"), {"new_password": YANGI_PAROL}, format="json")

        assert r.status_code == 204
        assert c.get(reverse("me")).data["has_password"] is True

    def test_boshqa_qurilmalar_uziladi(self, user: User) -> None:
        bu, boshqa = kirgan(user), kirgan(user)
        boshqa.get(reverse("me"))

        bu.post(
            reverse("me-password"),
            {"old_password": PAROL, "new_password": YANGI_PAROL},
            format="json",
        )

        assert chiqarilgan(boshqa)
        assert not chiqarilgan(bu)


@pytest.mark.django_db
class TestPochtaAlmashtirish:
    @pytest.fixture
    def egasi(self, user: User) -> User:
        user.email = "eski@example.com"
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email", "email_verified_at"])
        return user

    def boshla(self, user: User, email: str = "yangi@example.com", parol: str = PAROL) -> Any:
        return kirgan(user).post(
            reverse("me-email"), {"email": email, "password": parol}, format="json"
        )

    def test_tasdiqlanmaguncha_eski_manzil_qoladi(
        self, egasi: User, navbat: list[tuple[Any, ...]]
    ) -> None:
        assert self.boshla(egasi).status_code == 202

        egasi.refresh_from_db()
        assert egasi.email == "eski@example.com"
        name, *args = navbat[-1]
        assert name == "send_email_verify"
        assert args[-1] == "yangi@example.com", "kod YANGI manzilga boradi"

    def test_kod_bilan_almashadi_va_eski_manzilga_xabar_boradi(
        self, egasi: User, navbat: list[tuple[Any, ...]]
    ) -> None:
        self.boshla(egasi)
        _, _pk, _raw, code, _to = navbat[-1]

        r = APIClient().post(
            reverse("email-verify"), {"code": code, "username": egasi.username}, format="json"
        )

        assert r.status_code == 204
        egasi.refresh_from_db()
        assert egasi.email == "yangi@example.com"
        assert egasi.email_verified_at is not None
        assert navbat[-1] == ("send_email_changed", egasi.pk, "eski@example.com")

    def test_parol_notogri_bolsa_kod_yuborilmaydi(
        self, egasi: User, navbat: list[tuple[Any, ...]]
    ) -> None:
        assert self.boshla(egasi, parol="xato").status_code == 400
        assert navbat == []

    def test_kutish_paytida_manzil_band_bolsa_almashmaydi(
        self, egasi: User, other_user: User, navbat: list[tuple[Any, ...]]
    ) -> None:
        self.boshla(egasi)
        _, _pk, _raw, code, _to = navbat[-1]
        other_user.email = "yangi@example.com"
        other_user.save(update_fields=["email"])

        r = APIClient().post(
            reverse("email-verify"), {"code": code, "username": egasi.username}, format="json"
        )

        assert r.status_code == 400
        egasi.refresh_from_db()
        assert egasi.email == "eski@example.com"


@pytest.mark.django_db
class TestTaxallus:
    def almashtir(self, user: User, name: str, *, pay: bool = False) -> Any:
        return kirgan(user).post(
            reverse("me-username"), {"username": name, "pay": pay}, format="json"
        )

    def test_birinchi_almashtirish_bepul(self, user: User) -> None:
        r = self.almashtir(user, "yangi_nom")

        assert r.status_code == 200
        assert r.data["username"] == "yangi_nom"
        assert r.data["username_change"]["free_at"] is not None
        assert UsernameHistory.objects.filter(user=user, old_username="aziz").exists()

    def test_ikkinchisi_qvant_talab_qiladi(self, user: User) -> None:
        self.almashtir(user, "birinchi")

        r = self.almashtir(user, "ikkinchi")

        assert r.status_code == 400
        assert r.data["error"]["code"] == "payment_required"
        assert r.data["error"]["details"]["price"] == usernames.PRICE

    def test_qvant_bilan_tolanadi(self, user: User) -> None:
        self.almashtir(user, "birinchi")
        ledger.credit(user, usernames.PRICE + 100, QvantTransaction.Reason.ADMIN)

        r = self.almashtir(user, "ikkinchi", pay=True)

        assert r.status_code == 200
        assert ledger.get_wallet(user).balance == 100

    def test_balans_yetmasa_ozgarmaydi(self, user: User) -> None:
        self.almashtir(user, "birinchi")

        r = self.almashtir(user, "ikkinchi", pay=True)

        assert r.data["error"]["code"] == "insufficient_balance"
        user.refresh_from_db()
        assert user.username == "birinchi"

    def test_eski_nom_boshqaga_berilmaydi(self, user: User, other_user: User) -> None:
        self.almashtir(user, "yangi_nom")

        r = self.almashtir(other_user, "aziz")

        assert r.data["error"]["code"] == "reserved"

    def test_eski_nomni_egasi_qaytarib_oladi(self, user: User) -> None:
        self.almashtir(user, "yangi_nom")
        ledger.credit(user, usernames.PRICE, QvantTransaction.Reason.ADMIN)

        assert self.almashtir(user, "aziz", pay=True).status_code == 200

    def test_band_muddati_tugagach_beriladi(self, user: User, other_user: User) -> None:
        self.almashtir(user, "yangi_nom")
        UsernameHistory.objects.filter(user=user).update(
            changed_at=timezone.now() - UsernameHistory.RESERVE - timedelta(days=1)
        )

        assert self.almashtir(other_user, "aziz").status_code == 200

    def test_royxatdan_otishda_ham_band(self, user: User) -> None:
        self.almashtir(user, "yangi_nom")

        r = APIClient().post(
            reverse("register"),
            {
                "username": "aziz",
                "email": "x@example.com",
                "password": PAROL,
                # Roziliksiz 400 kelardi va test nom bandligini emas,
                # rozilikni o'lchab qolardi.
                "terms_accepted": True,
            },
            format="json",
        )
        check = APIClient().get(reverse("username-check"), {"u": "aziz"})

        assert r.status_code == 400
        assert check.data["available"] is False

    def test_eski_havola_yangi_profilni_beradi(self, user: User) -> None:
        self.almashtir(user, "yangi_nom")

        r = APIClient().get(reverse("user-detail", args=["aziz"]))

        assert r.status_code == 200
        assert r.data["username"] == "yangi_nom"

    def test_nuqtali_taxallus_profili_ochiladi(self, user: User) -> None:
        """Router'ning standart qolipi nuqtani kesib, profilni 404 qilardi."""
        self.almashtir(user, "ali.valiyev")

        assert APIClient().get(reverse("user-detail", args=["ali.valiyev"])).status_code == 200


@pytest.mark.django_db
class TestSessiyalar:
    def test_joriy_qurilma_belgilangan(self, user: User) -> None:
        r = kirgan(user).get(reverse("me-sessions"))

        assert r.status_code == 200
        assert [row["current"] for row in r.data] == [True]

    def test_boshqa_qurilmani_uzish(self, user: User) -> None:
        bu, boshqa = kirgan(user), kirgan(user)
        boshqa.get(reverse("me"))
        rows = bu.get(reverse("me-sessions")).data
        assert len(rows) == 2
        begona = next(row for row in rows if not row["current"])

        assert bu.delete(reverse("me-session", args=[begona["id"]])).status_code == 204
        assert chiqarilgan(boshqa)
        assert not chiqarilgan(bu)

    def test_hammasini_uzish_joriyni_qoldiradi(self, user: User) -> None:
        bu, a, b = kirgan(user), kirgan(user), kirgan(user)
        a.get(reverse("me"))
        b.get(reverse("me"))

        assert bu.delete(reverse("me-sessions")).status_code == 204
        assert chiqarilgan(a)
        assert chiqarilgan(b)
        assert not chiqarilgan(bu)

    def test_begona_sessiyani_uzib_bolmaydi(self, user: User, other_user: User) -> None:
        begona = kirgan(other_user)
        begona.get(reverse("me"))
        row = UserSession.objects.get(user=other_user)

        assert kirgan(user).delete(reverse("me-session", args=[row.pk])).status_code == 404
        assert not chiqarilgan(begona)


@pytest.mark.django_db
class TestAvatar:
    def yukla(self, client: APIClient, data: bytes = PNG) -> Any:
        return client.post(
            reverse("me-avatar"),
            {"file": SimpleUploadedFile("a.png", data, "image/png")},
            format="multipart",
        )

    def test_yuklanadi_va_beriladi(self, user: User, fake_s3: Any) -> None:
        r = self.yukla(kirgan(user))

        assert r.status_code == 200
        name = avatars.name_from_url(r.data["avatar_url"])
        assert name
        rasm = APIClient().get(reverse("avatar-file", args=[name]))
        assert rasm.status_code == 200
        assert rasm["Content-Type"] == "image/png"
        assert "immutable" in rasm["Cache-Control"]
        assert rasm.content == PNG

    def test_rasm_bolmagan_fayl_rad(self, user: User, fake_s3: Any) -> None:
        """Turi kengaytma yoki sarlavhaga emas, fayl imzosiga qarab aniqlanadi."""
        r = self.yukla(kirgan(user), b"<svg onload=alert(1)>")

        assert r.status_code == 400
        assert fake_s3.objects == {}

    def test_yangisi_eskisini_ochiradi(self, user: User, fake_s3: Any) -> None:
        c = kirgan(user)
        self.yukla(c)
        self.yukla(c)

        assert len(fake_s3.objects) == 1

    def test_ochirish(self, user: User, fake_s3: Any) -> None:
        c = kirgan(user)
        self.yukla(c)

        assert c.delete(reverse("me-avatar")).status_code == 204
        user.refresh_from_db()
        assert user.avatar_url == ""
        assert fake_s3.objects == {}

    def test_tashqi_manzil_profil_orqali_yozilmaydi(self, user: User) -> None:
        """Ixtiyoriy tashqi rasm har profil ko'rilishini uchinchi tomonga bildirardi."""
        kirgan(user).patch(
            reverse("me"), {"avatar_url": "https://kuzatuv.example/p.png"}, format="json"
        )

        user.refresh_from_db()
        assert user.avatar_url == ""

    def test_ulangan_hisobdan_olinadi(
        self, user: User, fake_s3: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        SocialAccount.objects.create(user=user, provider="github", uid="42", email="a@b.uz")
        olingan: list[str] = []

        def fetch(url: str) -> bytes:
            olingan.append(url)
            return PNG

        monkeypatch.setattr(avatars, "fetch_remote", fetch)

        r = kirgan(user).post(reverse("me-avatar-import"), {"provider": "github"}, format="json")

        assert r.status_code == 200
        assert olingan == ["https://avatars.githubusercontent.com/u/42?s=256"]
        assert len(fake_s3.objects) == 1

    def test_ulanmagan_hisobdan_olinmaydi(self, user: User) -> None:
        r = kirgan(user).post(reverse("me-avatar-import"), {"provider": "google"}, format="json")

        assert r.status_code == 400

    def test_ruxsatsiz_manzildan_olinmaydi(self) -> None:
        """SSRF: ichki tarmoq va shifrlanmagan manzil — ikkalasi ham rad."""
        with pytest.raises(avatars.AvatarError):
            avatars.fetch_remote("https://169.254.169.254/latest/meta-data")
        with pytest.raises(avatars.AvatarError):
            avatars.fetch_remote("http://lh3.googleusercontent.com/a.png")

    def test_google_rasmi_256_pikselda_soraladi(self) -> None:
        account = SocialAccount(
            provider="google", uid="1", picture="https://lh3.googleusercontent.com/a/x=s96-c"
        )

        assert avatars.provider_picture(account).endswith("=s256-c")


@pytest.mark.django_db
class TestProfilMaydonlari:
    def yoz(self, user: User, body: dict[str, Any]) -> Any:
        return kirgan(user).patch(reverse("me"), body, format="json")

    def test_malumotlar_saqlanadi(self, user: User) -> None:
        r = self.yoz(
            user,
            {
                "country": "uz",
                "region": "samarqand",
                "school": "1-maktab",
                "grade": "9-sinf",
                "website": "https://ali.dev",
                "birth_date": "2010-05-01",
            },
        )

        assert r.status_code == 200
        assert r.data["country"] == "UZ"

    def test_ozbekistonda_viloyat_royxatdan(self, user: User) -> None:
        assert self.yoz(user, {"country": "UZ", "region": "Atlantida"}).status_code == 400

    def test_boshqa_mamlakatda_viloyat_erkin(self, user: User) -> None:
        assert self.yoz(user, {"country": "KZ", "region": "Almaty"}).status_code == 200

    def test_kelajakdagi_tugilgan_kun_rad(self, user: User) -> None:
        ertaga = (timezone.localdate() + timedelta(days=1)).isoformat()

        assert self.yoz(user, {"birth_date": ertaga}).status_code == 400

    def test_faqat_maxfiy_maydonlar_yashiriladi(self, user: User) -> None:
        assert self.yoz(user, {"hidden_fields": ["email", "school"]}).status_code == 200
        assert self.yoz(user, {"hidden_fields": ["password"]}).status_code == 400

    def test_bildirishnoma_sozlamasi_tekshiriladi(self, user: User) -> None:
        togri = {"duel": {"site": True, "telegram": True}}

        assert self.yoz(user, {"notify_prefs": togri}).status_code == 200
        assert self.yoz(user, {"notify_prefs": {"nomalum": {"site": True}}}).status_code == 400
        assert self.yoz(user, {"notify_prefs": {"duel": {"email": True}}}).status_code == 400

    def test_korinish_sozlamasi_tekshiriladi(self, user: User) -> None:
        """Sxema v2 — guruhlangan (D33).

        Yassi shakl endi RAD ETILADI: `style` `appearance` guruhiga o'tdi.
        Bu ataylab — eski shaklni jimgina qabul qilish ikki xil saqlash
        yo'lini ochib qo'yardi va qaysi biri ustun ekani noaniq bo'lardi.
        """
        togri = {
            "appearance": {"style": "ocean", "size": 110, "density": "compact"},
            "a11y": {"vision": "protan", "bigTargets": True},
            "sound": True,
            "effect": "circle",
        }
        assert self.yoz(user, {"ui_prefs": togri}).status_code == 200

        # Noma'lum qiymatlar rad etiladi.
        assert self.yoz(user, {"ui_prefs": {"effect": "portlash"}}).status_code == 400
        # `size` qadami 5 (D45): 117 slayderda yo'q qiymat.
        assert self.yoz(user, {"ui_prefs": {"appearance": {"size": 117}}}).status_code == 400
        assert self.yoz(user, {"ui_prefs": {"appearance": {"theme": "system"}}}).status_code == 400
        # Eski yassi shakl ham rad etiladi.
        assert self.yoz(user, {"ui_prefs": {"style": "ocean"}}).status_code == 400

    def test_yangi_tillar_qabul_qilinadi(self, user: User) -> None:
        for locale in ("kaa", "kk", "ky", "tg", "tr", "zh", "es"):
            assert self.yoz(user, {"locale": locale}).status_code == 200, locale
