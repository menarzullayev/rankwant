"""Kunlik email kvota hisoblagichi — `core.mail_quota`.

Hisoblagich YANGI holat saqlamaydi: u `EmailDelivery` jadvalini o'qiydi.
Shuning uchun testlar ham shu jadvalga qator yozib, keyin `usage()` ni
chaqiradi — ya'ni tekshirilayotgan narsa «model to'g'rimi» emas,
«so'rov haqiqiy jadvaldan to'g'ri o'qiyaptimi».

Nega bu testlar kerak: 2026-09-17 da «1000 ta ro'yxat = 1000 ta xat»
savoli tekshirilganda kunlik shift 616 deb hisoblangan edi, aslida 700
(va Brevo navbati bilan 1700). Ya'ni kvota RAQAMI noto'g'ri bo'lsa,
butun reja noto'g'ri bo'ladi — shu sababli raqamlar ham qulflanadi.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from core import mail_quota
from core.models import EmailDelivery

pytestmark = pytest.mark.django_db


def _row(provider: str, status: str, *, days_ago: int = 0, to: str = "a@example.com"):
    """Bitta `EmailDelivery` qatori — vaqtni orqaga surib qo'yish mumkin."""
    row = EmailDelivery.objects.create(
        to_email=to,
        subject="s",
        provider=provider,
        status=status,
    )
    if days_ago:
        # `created_at` — `auto_now_add`, ya'ni `save()` uni qayta yozadi.
        # Shu sababli yangilash `queryset.update()` orqali (u `save()` ni
        # chetlab o'tadi).
        EmailDelivery.objects.filter(pk=row.pk).update(
            created_at=timezone.now() - timedelta(days=days_ago)
        )
    return row


def _sent(provider: str, n: int) -> None:
    for i in range(n):
        _row(provider, EmailDelivery.Status.SENT, to=f"u{i}@example.com")


class TestUsage:
    def test_bosh_jadval_hamma_provayderni_nol_bilan_korsatadi(self) -> None:
        rows = mail_quota.usage()

        assert [r.name for r in rows] == list(mail_quota.DAILY_QUOTA)
        assert all(r.sent == 0 for r in rows)
        assert all(r.remaining == r.quota for r in rows)

    def test_faqat_bugungi_sent_qatorlar_sanaladi(self) -> None:
        """Kechagi xat bugungi kvotani yemasligi kerak.

        Brevo/Mailjet/Resend kunlik shiftni kalendar kuni bo'yicha
        tiklaydi, ya'ni kechagi sarf bugun HISOBGA OLINMAYDI. Agar
        hisoblagich uni sanasa, «qoldi» doim kamroq ko'rinardi.
        """
        _row("brevo", EmailDelivery.Status.SENT, days_ago=1)
        _row("brevo", EmailDelivery.Status.SENT)  # bugun

        row = next(r for r in mail_quota.usage() if r.name == "brevo")

        assert row.sent == 1

    def test_failed_qatorlar_kvotani_yemasligi_kerak(self) -> None:
        """Yuborilmagan xat provayderda kvota SARFLAMAYDI.

        Zanjir butunlay yiqilganda `status=failed` yoziladi. Uni sanash
        kvotani soxta ravishda to'ldirardi — natijada «kvota tugadi» deb
        ogohlantirish chiqadi, aslida esa hech narsa yuborilmagan.
        """
        _row("brevo", EmailDelivery.Status.FAILED)
        _row("brevo", EmailDelivery.Status.FAILED)
        _row("brevo", EmailDelivery.Status.SENT)

        row = next(r for r in mail_quota.usage() if r.name == "brevo")

        assert row.sent == 1

    def test_skipped_qatorlar_kvotani_yemasligi_kerak(self) -> None:
        """Zaxira domenga «yuborilgan» xat kvota SARFLAMAYDI.

        Bu — 2026-09-17 hodisasining to'g'ridan-to'g'ri tekshiruvi: load
        test 301 ta `@example.invalid` manzilga xat yubordi, ular
        `status=sent` bo'lib yozildi va Brevo'ning 300/kun shiftini
        to'ldirdi. Panel «311 yuborildi» derdi, aslida 10 tasi haqiqiy.

        Endi bunday qatorlar `skipped` bo'ladi; `usage()` esa faqat
        `sent` ni sanaydi, ya'ni ular hisobga TUSHMASLIGI shart.
        """
        _row("brevo", EmailDelivery.Status.SKIPPED)
        _row("brevo", EmailDelivery.Status.SKIPPED)
        _row("brevo", EmailDelivery.Status.SENT)

        row = next(r for r in mail_quota.usage() if r.name == "brevo")

        assert row.sent == 1

    def test_skipped_qatorlar_yiqilish_deb_sanalmaydi(self) -> None:
        """`failures()` ham ularni ko'rmasligi kerak.

        O'tkazib yuborilgan xat — YIQILMAGAN xat. Aks holda panel
        «N xat yuborilmadi» deb qizil ko'rsatardi, holbuki hech qanday
        urinish bo'lmagan.
        """
        _row("brevo", EmailDelivery.Status.SKIPPED)

        assert mail_quota.failures() == 0

    def test_royxatda_yoq_provayder_ham_korinadi(self) -> None:
        """Yangi provayder qo'shilsa, sarfi jimgina yashirinmasin.

        `DAILY_QUOTA` da nom bo'lmasa `quota=0` bilan chiqadi — kvotasi
        noma'lum, lekin SARFI ko'rinadi.
        """
        _sent("yangi-provayder", 3)

        nomlar = {r.name: r for r in mail_quota.usage()}

        assert "yangi-provayder" in nomlar
        assert nomlar["yangi-provayder"].sent == 3
        assert nomlar["yangi-provayder"].configured is False


class TestHolatlar:
    def test_kvota_tugaganda_exhausted(self) -> None:
        _sent("resend", 100)

        row = next(r for r in mail_quota.usage() if r.name == "resend")

        assert row.exhausted is True
        assert row.remaining == 0
        assert row.lost == 0  # navbat yo'q, lekin hali oshib ketmagan

    def test_80_foizdan_keyin_ogohlantirish(self) -> None:
        _sent("resend", 80)

        row = next(r for r in mail_quota.usage() if r.name == "resend")

        assert row.warning is True
        assert row.exhausted is False

    def test_80_foizdan_oldin_ogohlantirish_yoq(self) -> None:
        """Salbiy tomoni: 79 ta xat hali «tugayapti» emas."""
        _sent("resend", 79)

        row = next(r for r in mail_quota.usage() if r.name == "resend")

        assert row.warning is False

    def test_kvotadan_oshgani_navbatga_tushadi(self) -> None:
        """Brevo: 300 to'g'ridan-to'g'ri + 1000 navbatga.

        350 ta xat = 300 yuborildi + 50 navbatda. HECH BIRI yo'qolmaydi.
        """
        _sent("brevo", 350)

        row = next(r for r in mail_quota.usage() if r.name == "brevo")

        assert row.exhausted is True
        assert row.in_queue is True
        assert row.lost == 0

    def test_navbat_ham_tolsa_xat_yoqoladi(self) -> None:
        """1300 dan keyin xat YETKAZILMAYDI — bu qizil holat."""
        _sent("brevo", 1310)

        row = next(r for r in mail_quota.usage() if r.name == "brevo")

        assert row.in_queue is False
        assert row.lost == 10

    def test_navbatsiz_provayder_uchun_in_queue_doim_false(self) -> None:
        """Resend'da navbat yo'q: 100 dan keyin xat yo'qoladi."""
        _sent("resend", 150)

        row = next(r for r in mail_quota.usage() if r.name == "resend")

        assert row.in_queue is False
        assert row.lost == 50


class TestJami:
    def test_bosh_jadvalda_jami_shift_700(self) -> None:
        """Qulflangan raqam: 300+200+100+100 = 700.

        616 emas — bu raqam ikki joyda xato edi (mailersend 16 deb
        olingan, brevo navbati hisobga olinmagan).
        """
        assert mail_quota.total_remaining() == 700

    def test_sarf_jami_shiftni_kamaytiradi(self) -> None:
        _sent("brevo", 10)
        _sent("mailjet", 5)

        assert mail_quota.total_remaining() == 700 - 15

    def test_navbat_hisobga_olinganda_1400(self) -> None:
        """Brevo kunligi tugagach navbat ochiladi: 700 - 300 + 1000 = 1400.

        Kun boshida bu raqam 700 bo'ladi (pastdagi test) — navbat hali
        ochilmagan. Ya'ni bu funksiya «hozir qancha yuborish mumkin» ni
        emas, «kunlik shift tugasa, yana qancha ochiladi» ni o'lchaydi.
        """
        _sent("brevo", 300)

        assert mail_quota.total_remaining_with_queue() == 1400

    def test_kvota_tugamagan_provayder_navbati_qoshilmaydi(self) -> None:
        """Navbat FAQAT kvota tugagandan keyin ochiladi.

        Aks holda «1700» raqami kun boshida ham ko'rinardi va u yolg'on
        bo'lardi — Brevo navbati hali ishga tushmagan. Ya'ni panel
        «bugun 1700 ta xat ketadi» deb va'da bermaydi; u o'sha 1000 ta
        navbatga faqat kunlik 300 tugagach haqiqatan kirishini ko'rsatadi.
        """
        _sent("brevo", 10)

        assert mail_quota.total_remaining_with_queue() == 700 - 10

    def test_navbat_tugagach_qoshimcha_ochilmaydi(self) -> None:
        """1300 dan keyin navbat ham to'ldi — jami o'smaydi.

        Aks holda panel cheksiz imkoniyat ko'rsatardi.
        """
        _sent("brevo", 1310)

        assert mail_quota.total_remaining_with_queue() == 400 + 1000

    def test_failures_bugungi_yiqilishlarni_sanaydi(self) -> None:
        _row("brevo", EmailDelivery.Status.FAILED)
        _row("resend", EmailDelivery.Status.FAILED, days_ago=1)

        assert mail_quota.failures() == 1

    def test_failures_bosh_jadvalda_nol(self) -> None:
        assert mail_quota.failures() == 0


class TestKunChegarasi:
    def test_day_start_utc_yarim_tun(self) -> None:
        """Kun chegarasi — UTC kalendar kuni (Resend shunday belgilaydi)."""
        now = timezone.now()
        start = mail_quota.day_start(now)

        assert (start.hour, start.minute, start.second, start.microsecond) == (0, 0, 0, 0)
        assert start.date() == now.date()

    def test_bugun_va_kecha_chegarasi_farq_qiladi(self) -> None:
        """Chegara haqiqatan ishlayaptimi — kechagi qator tashqarida."""
        _row("brevo", EmailDelivery.Status.SENT, days_ago=1)

        from django.utils import timezone as tz

        kecha = tz.now() - timedelta(days=1)

        assert mail_quota.total_remaining(kecha) == 700 - 1
        assert mail_quota.total_remaining() == 700

    def test_mahalliy_mintaqa_chegarani_siljitmaydi(self) -> None:
        """`TIME_ZONE` (Asia/Tashkent, UTC+5) chegarani 5 soatga surmasligi kerak.

        `datetime.replace()` mintaqani SAQLAB qoladi. Agar shunday qolsa,
        mahalliy yarim tun UTC 19:00 ga to'g'ri kelardi va 19:00 dan
        keyingi xatlar «kecha» hisoblanardi. Kun chegarasi esa
        provayderlarniki — UTC.
        """
        import datetime as dt

        tashkent = dt.timezone(timedelta(hours=5))
        mahalliy = dt.datetime(2026, 9, 17, 0, 30, tzinfo=tashkent)

        start = mail_quota.day_start(mahalliy)

        # Mahalliy 17-sentabr 00:30 = UTC 16-sentabr 19:30, ya'ni UTC
        # kun chegarasi 16-sentabr bo'lishi kerak — 17-sentabr emas.
        assert start == dt.datetime(2026, 9, 16, 0, 0, tzinfo=dt.UTC)


class TestWarningRows:
    """`warning_rows()` — ogohlantirish sharti yagona joyda.

    Nega alohida: vazifa ham, panel ham shu shartga tayanadi. Ikki joyda
    yozilsa ular vaqt o'tib ajralib ketadi va «panel qizil, xabar jim»
    holati paydo bo'ladi.
    """

    def test_bosh_jadvalda_ogohlantirish_yoq(self) -> None:
        assert mail_quota.warning_rows() == []

    def test_kvota_tugasa_qator_qaytadi(self) -> None:
        for i in range(300):
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        nomlar = [r.name for r in mail_quota.warning_rows()]

        assert nomlar == ["brevo"]

    def test_80_foizdan_kamida_jim(self) -> None:
        """Chegara ostida ogohlantirish YO'Q — aks holda xabar ma'nosiz bo'ladi."""
        for i in range(239):  # 239/300 = 79.7%
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        assert mail_quota.warning_rows() == []

    def test_80_foizda_ogohlantiradi(self) -> None:
        for i in range(240):  # 240/300 = 80%
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        assert [r.name for r in mail_quota.warning_rows()] == ["brevo"]

    def test_kvotasiz_provayder_ogohlantirmaydi(self) -> None:
        """`console` kvotasiz — u hech qachon «tugamaydi»."""
        _row("console", EmailDelivery.Status.SENT)

        assert mail_quota.warning_rows() == []


class TestSummary:
    """`summary()` — odam o'qiy oladigan matn.

    Matn bildirishnomaga tushadi, ya'ni u BO'SH bo'lmasligi va eng muhim
    raqamni ko'rsatishi kerak. Bo'sh matn chaqiruvchida «hammasi joyida»
    degan ma'no beradi.
    """

    def test_bosh_jadvalda_bosh_matn(self) -> None:
        assert mail_quota.summary() == ""

    def test_tugagan_kvota_matnda_korinadi(self) -> None:
        for i in range(305):  # 300 dan oshdi — navbatda
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        matn = mail_quota.summary()

        assert "brevo" in matn
        assert "tugadi" in matn

    def test_yetkazilmagan_xat_matnda_bold_korinadi(self) -> None:
        """`lost` — eng og'ir holat: navbat ham to'ldi, xat YO'QOLADI."""
        for i in range(1301):
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        matn = mail_quota.summary()

        assert "YETKAZILMAYDI" in matn

    def test_kunlik_qoldiq_matnda_bor(self) -> None:
        """Matn «yana qancha mumkin» raqamini ham beradi — qaror shunga tayanadi."""
        for i in range(300):
            _row("brevo", EmailDelivery.Status.SENT, to=f"u{i}@example.com")

        # 400 qoldi (mailjet 200 + resend 100 + mailersend 100).
        assert "400" in mail_quota.summary()
