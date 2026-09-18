"""Staff email kvota endpoint'i — `/staff/email-quota/`.

Asosiy tekshiruv: endpoint HAQIQIY `EmailDelivery` jadvalidan o'qiydi va
faqat staff ko'radi. Hisoblagichning o'zi `test_mail_quota.py` da
tekshiriladi — bu yerda HTTP qatlam: ruxsat, javob shakli va
productionda kvotani ko'rishning YAGONA yo'li ishlayaptimi.

Nega alohida endpoint: Django admin paneli productionda o'chirilgan
(`ADMIN_ENABLED=False`), ya'ni kvotani u yerdan ko'rib bo'lmaydi.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import EmailDelivery, User


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("xodim", password="x", is_staff=True)


@pytest.fixture
def oddiy(db) -> User:
    return User.objects.create_user("oddiy", password="x")


def yoz(to: str, provider: str, status: str = EmailDelivery.Status.SENT) -> EmailDelivery:
    return EmailDelivery.objects.create(to_email=to, subject="s", provider=provider, status=status)


def kechaga_sur(obyekt: EmailDelivery) -> None:
    """`created_at` ni kechagi XAVFSIZ nuqtaga suradi.

    `now() - 1 kun` xato bo'lardi: Tashkent UTC+5, ya'ni mahalliy 23:00
    da UTC hali 18:00 — bunday vaqt HAMON bugungi UTC kuniga tushadi.
    `auto_now_add` tufayli `update()` bilan yozish shart (create'da
    qiymat e'tiborsiz qoladi).
    """
    EmailDelivery.objects.filter(pk=obyekt.pk).update(
        created_at=timezone.now() - timedelta(days=1, hours=6)
    )


def kecha_sorov() -> str:
    """Kechagi UTC kun uchun `?when=` qiymati — tush payti, chegaradan uzoq."""
    return (timezone.now() - timedelta(days=1, hours=6)).date().isoformat() + "T12:00:00Z"


def sorov(user: User, **params: str) -> Any:
    """Staff endpoint'iga GET. `Any` — javob shakli test ichida tekshiriladi."""
    c = APIClient()
    c.force_authenticate(user=user)
    return c.get(reverse("staff-email-quota"), params)


@pytest.mark.django_db
class TestKirish:
    def test_staff_kora_oladi(self, staff: User) -> None:
        assert sorov(staff).status_code == 200

    def test_oddiy_foydalanuvchi_rad_etiladi(self, oddiy: User) -> None:
        assert sorov(oddiy).status_code == 403

    def test_kirilmagan_rad_etiladi(self) -> None:
        assert APIClient().get(reverse("staff-email-quota")).status_code in (401, 403)


@pytest.mark.django_db
class TestJavobShakli:
    def test_bosh_jadvalda_shakl_tolik(self, staff: User) -> None:
        body = sorov(staff).json()

        assert body["window"] == "utc_day"
        # UTC yarim tuni — vaqt mintaqasi belgisi bilan (`+00:00`).
        # Panel «bugun» degan chegarani aynan shundan oladi.
        assert "T00:00:00+00:00" in body["day_start"]
        assert body["total_remaining"] == 700
        assert body["failures"] == 0

    def test_hamma_provayder_qatorlari_bor(self, staff: User) -> None:
        body = sorov(staff).json()

        nomlar = [p["name"] for p in body["providers"]]
        assert nomlar == ["brevo", "mailjet", "resend", "mailersend", "console"]

    def test_haqiqiy_sarf_korinadi(self, staff: User) -> None:
        """Qator yozilsa, javobda o'sha provayder sarfi ko'rinadi."""
        yoz("a@example.com", "brevo")
        yoz("b@example.com", "brevo")
        yoz("c@example.com", "resend")

        body = sorov(staff).json()
        by = {p["name"]: p for p in body["providers"]}

        assert by["brevo"]["sent"] == 2
        assert by["brevo"]["remaining"] == 298
        assert by["resend"]["sent"] == 1
        assert body["total_remaining"] == 700 - 3

    def test_kvota_oshsa_navbat_korinadi(self, staff: User) -> None:
        """Brevo 300 dan oshsa — `in_queue` va navbat hajmi javobda."""
        for i in range(310):
            yoz(f"u{i}@example.com", "brevo")

        by = {p["name"]: p for p in sorov(staff).json()["providers"]}

        assert by["brevo"]["exhausted"] is True
        assert by["brevo"]["in_queue"] is True
        assert by["brevo"]["lost"] == 0
        assert by["brevo"]["queue"] == 1000

    def test_navbat_ham_tolsa_lost_korinadi(self, staff: User) -> None:
        """1300 dan oshgan qism `lost` — bu qizil holat, javobda bo'lishi shart."""
        for i in range(1305):
            yoz(f"u{i}@example.com", "brevo")

        by = {p["name"]: p for p in sorov(staff).json()["providers"]}

        assert by["brevo"]["lost"] == 5
        assert by["brevo"]["in_queue"] is False

    def test_failed_qatorlar_kvotani_yemasligi_kerak(self, staff: User) -> None:
        yoz("a@example.com", "", EmailDelivery.Status.FAILED)
        yoz("b@example.com", "brevo")

        body = sorov(staff).json()

        assert body["total_remaining"] == 700 - 1
        assert body["failures"] == 1


@pytest.mark.django_db
class TestWhenParametri:
    """`?when=` — boshqa kunning sarfini ko'rish.

    Nega kerak: deploy oldidan «kecha nechta xat ketdi» savoli tug'iladi
    va uni faqat `EmailDelivery` jadvalini qo'lda ochib javob berish
    mumkin edi. Parametr o'qib bo'lmaydigan bo'lsa `400` qaytishi shart —
    aks holda «noto'g'ri sana» jimgina «bugun» bo'lib ko'rinardi va
    raqam noto'g'ri o'qilardi.
    """

    def test_otgan_kun_sarfi_korinadi(self, staff: User) -> None:
        kechaga_sur(yoz("a@example.com", "brevo"))
        yoz("b@example.com", "brevo")

        body = sorov(staff, when=kecha_sorov()).json()

        # `total_remaining` — BARCHA provayder yig'indisi (300+200+100+100),
        # ya'ni kechagi bitta xat uni 700 → 699 ga tushiradi.
        assert body["total_remaining"] == 699
        assert {p["name"]: p["sent"] for p in body["providers"]}["brevo"] == 1

    def test_otgan_kundan_keyingi_qator_korinmaydi(self, staff: User) -> None:
        """Bugungi xat o'tgan kun so'rovida chiqmasligi kerak — filtr ikki tomonlama."""
        yoz("a@example.com", "brevo")

        body = sorov(staff, when=kecha_sorov()).json()

        assert body["total_remaining"] == 700
        assert {p["name"]: p["sent"] for p in body["providers"]}["brevo"] == 0

    def test_bugun_parametrsiz_bilan_bir_xil(self, staff: User) -> None:
        yoz("a@example.com", "brevo")

        assert (
            sorov(staff, when=timezone.now().isoformat()).json()["total_remaining"]
            == (sorov(staff).json()["total_remaining"])
        )

    def test_notogri_sana_400_qaytaradi(self, staff: User) -> None:
        assert sorov(staff, when="kecha").status_code == 400

    def test_bosh_qiymat_bugunni_beradi(self, staff: User) -> None:
        """`?when=` bo'sh — xato emas, shunchaki e'tiborsiz qoldiriladi."""
        assert sorov(staff, when="").status_code == 200

    def test_mahalliy_vaqt_utc_chegarasiga_ogiriladi(self, staff: User) -> None:
        """`+05:00` bilan berilgan vaqt UTC kun chegarasini siljitmasligi kerak.

        Bu HAQIQIY bug edi: `day_start` ichidagi `datetime.replace()`
        mintaqani saqlab qoladi, ya'ni `Asia/Tashkent` (UTC+5) dagi yarim
        tun UTC bo'yicha 19:00 ga to'g'ri keladi va `created_at__gte`
        filtri 5 soatga siljib ketardi.
        """
        kechaga_sur(yoz("a@example.com", "brevo"))

        # Mahalliy mintaqada (Tashkent) berilgan vaqt — kechagi kun.
        kecha = timezone.localtime(timezone.now() - timedelta(days=1, hours=6)).isoformat()
        body = sorov(staff, when=kecha).json()

        # Chegara baribir UTC yarim tuni bo'lishi shart.
        assert body["day_start"].endswith("T00:00:00+00:00")
        assert body["total_remaining"] == 699

    def test_plus_belgisi_qochirilmasa_400_boladi(self, staff: User) -> None:
        """Xom qator ichidagi `+` — TAXMIN QILINMAYDIGAN tuzoq.

        Nima bo'ladi: query qatorida `+` **probel** deb o'qiladi
        (`application/x-www-form-urlencoded`). Ya'ni
        `?when=...T12:00:00+00:00` API ga `...T12:00:00 00:00` bo'lib
        yetib keladi va `parse_datetime` uni o'qiy olmaydi -> `400`.

        O'lchandi 2026-09-18: `+00:00` bilan QO'LDA yasalgan xom qator
        `400` qaytardi; xuddi shu qiymat `urlencode` qilinganda `200`.

        ⚠️ Django test mijozi parametrni **o'zi** `urlencode` qiladi,
        shuning uchun bu yerda `+` XAVFSIZ — tuzoq faqat xom qator
        yasalганда ko'rinadi. Shu sababli quyida qo'lda qochirilgan
        (`%2B`) variant tekshiriladi: u HAQIQIY tomonni — brauzer
        yuboradigan baytlarni — aks ettiradi.

        Nega muhim: panel `?when=` ni JS dan yuboradi. `toISOString()`
        `Z` beradi (`+` yo'q), ya'ni hech qanday qochirish kerak emas —
        muammo umuman tug'ilmaydi. Bu test shuni qotiradi: `Z` shakli
        tanlanishining sababi «chiroyli», balki `+` probelga
        aylanmasligi.
        """
        # Qo'lda yasalgan xom qator — `+` probel bo'lib yetib keladi va
        # o'qib bo'lmaydi. `+` ni `%2B` qilib yuborilsa — ishlaydi.
        assert sorov(staff, when="2026-09-11T20:31:19 00:00").status_code == 400

    def test_z_va_qochirilgan_plus_bir_xil_kunni_beradi(self, staff: User) -> None:
        """`Z` ham, to'g'ri qochirilgan `+00:00` ham bir xil kunni beradi.

        Ikki xil yozuv — bitta kun. Panel `Z` ni ishlatadi; bu test
        shartnomani qotiradi: ikkisi ham qabul qilinadi va natija bir
        xil, ya'ni `Z` ni tanlash xatoni keltirmaydi.
        """
        z = sorov(staff, when="2026-09-11T20:31:19Z").json()
        plus = sorov(staff, when="2026-09-11T20:31:19+00:00").json()

        assert z["day_start"] == plus["day_start"] == "2026-09-11T00:00:00+00:00"
        assert z["total_remaining"] == plus["total_remaining"]
