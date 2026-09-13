"""Hisob xatlarining o'zi — ADR-0015.

Bu yerda zanjir soxtalashtiriladi (u `test_mailer.py` da sinalgan) va
faqat XAT tekshiriladi: uch tilda to'g'ri satrlar, havolaning bizning
domenimizda qolishi, matnli nusxaning mavjudligi.
"""

from __future__ import annotations

from typing import Any

import pytest

from core import emails
from core.mail_providers import Message
from core.models import EmailDelivery, User


class Yozib:
    """Zanjir o'rniga — yuborilgan xabarni ushlab qoladi."""

    name = "yozib"
    configured = True

    def __init__(self) -> None:
        self.last: Message | None = None

    def send(self, msg: Message) -> None:
        self.last = msg


@pytest.fixture
def zanjir(monkeypatch: pytest.MonkeyPatch, settings: Any) -> Yozib:
    p = Yozib()
    monkeypatch.setattr("core.mailer.PROVIDERS", {p.name: p})
    settings.EMAIL_CHAIN = [p.name]
    settings.SITE_URL = "https://rankwant.uz"
    return p


def odam(locale: str = "uz") -> User:
    return User.objects.create_user(
        username=f"u_{locale}", email=f"{locale}@example.com", password="Parol!12345", locale=locale
    )


@pytest.mark.django_db
class TestParolniTiklash:
    def test_yuboriladi_va_yoziladi(self, zanjir: Yozib) -> None:
        row = emails.send_password_reset(odam(), token="TOK", code="482913", request_ip="1.2.3.4")

        assert row.status == EmailDelivery.Status.SENT
        assert row.purpose == EmailDelivery.Purpose.PASSWORD_RESET
        assert zanjir.last is not None

    def test_havola_bizning_domenda_qoladi(self, zanjir: Yozib) -> None:
        """Kuzatuv o'chirilgan (ADR-0015): foydalanuvchi manzilda `rankwant`
        so'zini ko'rishi va ko'rmasa shubhalanishi kerak.

        Kanonik manzil — `/login?tab=reset-password&token=…` (1 va
        13-qarorlar). Tartib MUHIM EMAS, ya'ni `&` va `?` almashib ketsa
        test yiqilmasligi kerak — shuning uchun ikkala qism alohida
        tekshiriladi.
        """
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        assert "https://rankwant.uz/login?" in zanjir.last.html
        assert "tab=reset-password" in zanjir.last.html
        assert "token=TOK" in zanjir.last.html
        for begona in ("mailjet.com", "brevo.com", "resend.com", "mailersend.com"):
            assert begona not in zanjir.last.html

    def test_kod_ikkala_nusxada_ham_bor(self, zanjir: Yozib) -> None:
        """Matnli nusxa shart: mijoz HTML ni ko'rsatmasa ham kod qolishi kerak."""
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        assert "482913" in zanjir.last.html
        assert "482913" in zanjir.last.text
        assert zanjir.last.text.strip()

    def test_tab_va_token_birgalikda(self, zanjir: Yozib) -> None:
        """`_context` ikkala parametrni bitta so'rov satriga yig'adi.

        Token bo'lmasa `?tab=` yolg'iz qoladi va ortiqcha `&` chiqmaydi;
        ikkalasi bo'lsa tartib `tab` → `token` (barqaror test uchun).
        Kod (6 xonali) esa havolaga umuman tushmaydi — u faqat qo'lda
        kiritish uchun.
        """
        from core import email_text
        from core.emails import _context

        # Bitta foydalanuvchi: `odam()` har chaqiruvda yangi qator yasaydi
        # va bir xil `username` bilan ikkinchisi IntegrityError beradi.
        egasi = odam()

        def havola(**kwargs: str) -> object:
            return _context(email_text.CHANGED, egasi, **kwargs)["link"]  # type: ignore[arg-type]

        assert (
            havola(path="/login", tab="reset-password", token="", code="")
            == "https://rankwant.uz/login?tab=reset-password"
        )

        assert (
            havola(path="/login", tab="reset-password", token="TOK", code="482913")
            == "https://rankwant.uz/login?tab=reset-password&token=TOK"
        )

        assert (
            havola(path="/verify-email", token="TOK", code="482913")
            == "https://rankwant.uz/verify-email?token=TOK"
        )

    def test_kontekst_korsatiladi(self, zanjir: Yozib) -> None:
        emails.send_password_reset(
            odam(), token="TOK", code="482913", request_ip="9.9.9.9", request_ua="Firefox"
        )

        assert zanjir.last is not None
        assert "9.9.9.9" in zanjir.last.html
        assert "Firefox" in zanjir.last.html

    @pytest.mark.parametrize(
        ("locale", "kutilgan"),
        [
            ("uz", "parolni tiklash"),
            ("ru", "восстановление пароля"),
            ("en", "password reset"),
        ],
    )
    def test_foydalanuvchi_tilida(self, zanjir: Yozib, locale: str, kutilgan: str) -> None:
        emails.send_password_reset(odam(locale), token="TOK", code="482913")

        assert zanjir.last is not None
        assert kutilgan in zanjir.last.subject.lower()

    def test_notanish_til_ozbekchaga_tushadi(self, zanjir: Yozib) -> None:
        user = odam()
        User.objects.filter(pk=user.pk).update(locale="de")
        user.refresh_from_db()

        emails.send_password_reset(user, token="TOK", code="482913")

        assert zanjir.last is not None
        assert "parolni tiklash" in zanjir.last.subject.lower()


@pytest.mark.django_db
class TestEmailniTasdiqlash:
    def test_boshqa_maqsad_va_boshqa_yol(self, zanjir: Yozib) -> None:
        row = emails.send_email_verify(odam(), token="TOK", code="123456")

        assert row.purpose == EmailDelivery.Purpose.EMAIL_VERIFY
        assert zanjir.last is not None
        assert "/verify-email?token=TOK" in zanjir.last.html

    def test_kontekst_korsatilmaydi(self, zanjir: Yozib) -> None:
        """Foydalanuvchi bu so'rovni o'zi, shu daqiqada yubordi — «bu men
        emasman» degan savol tug'ilmaydi, ya'ni IP ham keraksiz."""
        emails.send_email_verify(odam(), token="TOK", code="123456")

        assert zanjir.last is not None
        assert "IP:" not in zanjir.last.html


@pytest.mark.django_db
class TestShablon:
    def test_logotip_bloklansa_brend_matn_bolib_qoladi(self, zanjir: Yozib) -> None:
        """Email mijozlari rasmni odatda bloklaydi (ADR-0015)."""
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        assert 'alt="RankWant"' in zanjir.last.html
        # Rasmdan TASHQARI ham brend nomi matn sifatida turadi.
        assert zanjir.last.html.count("RankWant") > 1

    def test_qorongi_rejim_qoidalari_bor(self, zanjir: Yozib) -> None:
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        assert "prefers-color-scheme: dark" in zanjir.last.html
        assert 'name="color-scheme"' in zanjir.last.html

    def test_kuzatuv_pikseli_yoq(self, zanjir: Yozib) -> None:
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        rasmlar = zanjir.last.html.count("<img")
        assert rasmlar == 1, "faqat logotip bo'lishi kerak"

    def test_shablon_izohlari_xatga_chiqmaydi(self, zanjir: Yozib) -> None:
        """Django'da `{# … #}` FAQAT bitta qatorda ishlaydi.

        Ko'p qatorli yozilganda u izoh deb tanilmaydi va oddiy matn bo'lib
        chiqadi. O'lchandi: mening ichki izohlarim uchta haqiqiy xatning
        tanasida foydalanuvchiga ko'rinib turdi.
        """
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        for qoldiq in ("{#", "#}", "{%", "%}", "{{", "}}"):
            assert qoldiq not in zanjir.last.html, qoldiq
            assert qoldiq not in zanjir.last.text, qoldiq

    def test_matnli_nusxada_html_yoq(self, zanjir: Yozib) -> None:
        emails.send_password_reset(odam(), token="TOK", code="482913")

        assert zanjir.last is not None
        assert "<" not in zanjir.last.text


def test_notanish_til_lugatni_yiqitmaydi() -> None:
    from core import email_text

    assert email_text.strings(email_text.RESET, "de")["subject"].startswith("RankWant")


def test_barcha_satrlar_uch_tilda(*_: Any) -> None:
    """Bitta tarjima unutilsa xat yarim o'zbekcha bo'lib chiqardi."""
    from core import email_text

    for jadval in (email_text.SHARED, email_text.RESET, email_text.VERIFY):
        for kalit, qiymatlar in jadval.items():
            assert set(qiymatlar) == {"uz", "ru", "en"}, kalit
