"""Email zanjiri — birinchi ishlagani g'olib, qolgani yozib qolinadi.

Zanjir bepul planlar ustiga qurilgan: Brevo 300/kun, Mailjet 200/kun,
Resend 100/kun, MailerSend 500/oy. «Kvota tugadi» — kundalik hodisa,
ya'ni tushib qolish NORMAL yo'l, istisno emas.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from io import BytesIO
from typing import Any

import pytest
from django.test import override_settings

from core.mail_providers import PROVIDERS, Mailjet, Message, SendError
from core.mailer import send_email
from core.models import EmailDelivery


class FakeProvider:
    """Zanjir mantig'ini sinash uchun — tarmoqqa chiqmaydi."""

    def __init__(self, name: str, *, ok: bool = True, configured: bool = True) -> None:
        self.name = name
        self.ok = ok
        self.configured = configured
        self.calls: list[Message] = []

    def send(self, msg: Message) -> None:
        self.calls.append(msg)
        if not self.ok:
            raise SendError("HTTP 429: kvota tugadi")


@pytest.fixture
def chain(monkeypatch: pytest.MonkeyPatch):
    """`PROVIDERS` ni almashtiradi va zanjirni uchtaga qisqartiradi."""

    def build(*providers: FakeProvider):
        monkeypatch.setattr("core.mailer.PROVIDERS", {p.name: p for p in providers})
        return override_settings(EMAIL_CHAIN=[p.name for p in providers])

    return build


@pytest.mark.django_db
class TestZanjir:
    def test_birinchisi_ishlasa_qolganiga_tegilmaydi(self, chain: Any) -> None:
        birinchi, ikkinchi = FakeProvider("brevo"), FakeProvider("mailjet")

        with chain(birinchi, ikkinchi):
            row = send_email(to="a@rankwant.uz", subject="salom", text="matn")

        assert row.status == EmailDelivery.Status.SENT
        assert row.provider == "brevo"
        assert row.attempts == []
        assert len(birinchi.calls) == 1
        assert ikkinchi.calls == []

    def test_kvota_tugasa_keyingisiga_otadi(self, chain: Any) -> None:
        birinchi = FakeProvider("brevo", ok=False)
        ikkinchi = FakeProvider("mailjet")

        with chain(birinchi, ikkinchi):
            row = send_email(to="a@rankwant.uz", subject="salom", text="matn")

        assert row.status == EmailDelivery.Status.SENT
        assert row.provider == "mailjet"
        # Nega birinchisi tushib qolgani yozib qolinadi — «email kelmadi»
        # shikoyatini shusiz tekshirib bo'lmaydi.
        assert row.attempts == [{"provider": "brevo", "error": "HTTP 429: kvota tugadi"}]
        assert len(ikkinchi.calls) == 1

    def test_kalitsiz_provayder_tushib_qoladi(self, chain: Any) -> None:
        yoq = FakeProvider("brevo", configured=False)
        bor = FakeProvider("resend")

        with chain(yoq, bor):
            row = send_email(to="a@rankwant.uz", subject="salom", text="matn")

        assert row.provider == "resend"
        # Sozlanmagan provayder URINISH emas: u xato qilmadi, umuman
        # chaqirilmadi. Aks holda log har safar soxta xato bilan to'ladi.
        assert row.attempts == []
        assert yoq.calls == []

    def test_hammasi_yiqilsa_yozuv_failed_boladi(self, chain: Any) -> None:
        with chain(FakeProvider("brevo", ok=False), FakeProvider("mailjet", ok=False)):
            row = send_email(to="a@rankwant.uz", subject="salom", text="matn")

        assert row.status == EmailDelivery.Status.FAILED
        assert row.provider == ""
        assert [a["provider"] for a in row.attempts] == ["brevo", "mailjet"]

    def test_yaroqsiz_manzil_zanjirga_kirmaydi(self, chain: Any) -> None:
        birinchi = FakeProvider("brevo")

        with chain(birinchi):
            row = send_email(to="manzil-emas", subject="salom", text="matn")

        assert row.status == EmailDelivery.Status.FAILED
        assert birinchi.calls == []

    def test_xat_tanasi_bazaga_yozilmaydi(self, chain: Any) -> None:
        """Parol tiklash havolasi — token; uni bazaga ko'chirmaymiz."""
        with chain(FakeProvider("brevo")):
            send_email(
                to="a@rankwant.uz",
                subject="Parolni tiklash",
                text="https://rankwant.uz/reset/SIRLI-TOKEN",
                purpose=EmailDelivery.Purpose.PASSWORD_RESET,
            )

        row = EmailDelivery.objects.get()
        assert "SIRLI-TOKEN" not in json.dumps(
            {"s": row.subject, "a": row.attempts, "p": row.provider}
        )


@pytest.mark.django_db
class TestZaxiraDomen:
    """RFC 2606/6761 manzillarga provayderga UMUMAN murojaat qilinmaydi.

    Nega kerak: 2026-09-17 da load test 301 ta `@example.invalid` manzilga
    xat «yubordi» va Brevo'ning 300/kun bepul shiftini 85 soniyada yoqib
    yubordi — haqiqiy foydalanuvchilarning xatlari navbatga tushdi.
    Panel «311 yuborildi» derdi, aslida 10 tasi haqiqiy edi.

    Zaxira domen — RFC 2606/6761 bo'yicha hech qachon mavjud bo'lmaydigan
    nom, ya'ni unga yuborish faqat zarar keltiradi: xat yetib bormaydi,
    kvota esa yonadi.
    """

    def test_provayderga_umuman_murojaat_qilinmaydi(self, chain: Any) -> None:
        birinchi = FakeProvider("brevo")

        with chain(birinchi):
            row = send_email(to="loadtest-1@example.invalid", subject="s", text="t")

        # Eng muhim tasdiq: kvota yonmaydi.
        assert birinchi.calls == []
        assert row.status == EmailDelivery.Status.SKIPPED
        assert row.provider == ""
        assert row.attempts == [{"provider": "", "error": "zaxira domen — yuborilmadi"}]

    @pytest.mark.parametrize(
        "manzil",
        ["a@example.com", "a@example.invalid", "a@example.org", "a@localhost"],
    )
    def test_zaxira_domenlar_har_xil_korinishda(self, chain: Any, manzil: str) -> None:
        birinchi = FakeProvider("brevo")
        with chain(birinchi):
            row = send_email(to=manzil, subject="s", text="t")
        assert row.status == EmailDelivery.Status.SKIPPED
        assert birinchi.calls == []

    def test_yaroqsiz_manzil_ham_provayderga_chiqmaydi(self, chain: Any) -> None:
        """`a@test` — `SKIPPED` emas, `FAILED`. Muhimi bir xil.

        O'lchandi 2026-09-18: `is_placeholder("a@test")` — `True`, LEKIN
        Django `validate_email` bir bo'g'inli domenni rad etadi, ya'ni
        qator validatsiya shoxobchasida `FAILED` bo'ladi va zaxira domen
        tekshiruviga yetib bormaydi.

        Ikkala yo'l ham bir xil muhim shartni bajaradi: **provayder
        chaqirilmaydi**, ya'ni kvota yonmaydi. Shu sababli bu yerda holat
        emas, o'sha shart tekshiriladi.
        """
        birinchi = FakeProvider("brevo")
        with chain(birinchi):
            row = send_email(to="a@test", subject="s", text="t")
        assert row.status == EmailDelivery.Status.FAILED
        assert birinchi.calls == []

    def test_ruxsat_berilsa_yuboriladi(self, chain: Any) -> None:
        """`send_test_email` shu yo'ldan yuradi.

        U provayderning javobini ko'rish uchun ATAYLAB zaxira domenga
        yuboradi (`siz@example.com` — hujjatida shunday yozilgan), ya'ni
        to'sish o'sha ish qurolini sindirardi.
        """
        birinchi = FakeProvider("brevo")

        with chain(birinchi):
            row = send_email(to="siz@example.com", subject="s", text="t", allow_placeholder=True)

        assert row.status == EmailDelivery.Status.SENT
        assert row.provider == "brevo"
        assert len(birinchi.calls) == 1

    def test_oddiy_manzil_ozgarmaydi(self, chain: Any) -> None:
        """Nazorat: haqiqiy manzil avvalgidek zanjirdan o'tadi.

        Usiz yuqoridagi testlar «hamma narsani o'tkazib yuboradigan»
        soxta tekshiruvni ham yashil qoldirardi.
        """
        birinchi = FakeProvider("brevo")

        with chain(birinchi):
            row = send_email(to="a@rankwant.uz", subject="s", text="t")

        assert row.status == EmailDelivery.Status.SENT
        assert row.provider == "brevo"
        assert len(birinchi.calls) == 1


@pytest.mark.django_db
class TestMailjetJavobi:
    """Mailjet v3.1 xato bo'lganda ham HTTP 200 qaytaradi."""

    def _javob(self, monkeypatch: pytest.MonkeyPatch, payload: dict) -> None:
        monkeypatch.setattr(
            urllib.request,
            "urlopen",
            lambda *a, **k: BytesIO(json.dumps(payload).encode()),
        )

    def test_ichki_xato_yiqilish_deb_hisoblanadi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._javob(monkeypatch, {"Messages": [{"Status": "error"}]})

        with (
            override_settings(MAILJET_API_KEY="k", MAILJET_SECRET_KEY="s"),
            pytest.raises(SendError),
        ):
            Mailjet().send(Message(to="a@example.com", subject="s", text="t"))

    def test_success_qabul_qilinadi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._javob(monkeypatch, {"Messages": [{"Status": "success"}]})

        with override_settings(MAILJET_API_KEY="k", MAILJET_SECRET_KEY="s"):
            Mailjet().send(Message(to="a@example.com", subject="s", text="t"))


@pytest.mark.django_db
class TestHttpXatosi:
    def test_4xx_zanjirni_toxtatmaydi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """422 va 401 XABARDA emas, PROVAYDERDA muammo.

        MailerSend tasdiqlanmagan akkauntda 422, eskirgan kalit 401
        qaytaradi — ikkalasida ham keyingi provayder yuborishi mumkin.
        """

        def yiqiladi(*a: Any, **k: Any):
            raise urllib.error.HTTPError("u", 422, "no", {}, BytesIO(b"trial account"))  # type: ignore[arg-type]

        monkeypatch.setattr(urllib.request, "urlopen", yiqiladi)

        with (
            override_settings(
                EMAIL_CHAIN=["mailersend", "console"],
                MAILERSEND_API_KEY="k",
                DEBUG=True,
            ),
        ):
            row = send_email(to="a@rankwant.uz", subject="s", text="t")

        assert row.status == EmailDelivery.Status.SENT
        assert row.provider == "console"
        assert row.attempts[0]["provider"] == "mailersend"


class TestSozlash:
    def test_zanjirdagi_hamma_nom_mavjud(self) -> None:
        """`EMAIL_CHAIN` ning standart qiymati jimgina buzilmasin."""
        from django.conf import settings

        assert set(settings.EMAIL_CHAIN) <= set(PROVIDERS)
