"""Kunlik kvota ogohlantirishi — `core.warn_email_quota`.

Panel (`/staff/email-quota/`) kvotani KO'RSATADI, lekin uni ochish kerak.
Bu vazifa esa o'zi aytadi — ya'ni xodim panelni ochmasa ham kvota
tugayotganini biladi.

Nega bu testlar alohida: `test_mail_quota.py` faqat HISOBLAGICHNI
tekshiradi (qaysi qator «e'tibor talab qiladi»). Bu yerda tekshiriladigan
narsa boshqacha — vazifa haqiqiy bildirishnoma YARATADIMI, uni KIMGA
yaratadi, va bir kunda faqat BIR MARTA yaratadimi.

Eng nozik joy — `notifications.notify()` ATAYLAB ishlatilmaydi. U
foydalanuvchi sozlamasini hurmat qiladi, xodim esa bu xabarni o'chirib
qo'yishi mumkin. Xato bo'lsa kvota jimgina tugaydi, ya'ni
ogohlantirishning o'zi yo'qoladi. Shu sababli bu yerda alohida test bor:
`notify_prefs` o'chirilgan bo'lsa ham xabar KELISHI kerak.
"""

from __future__ import annotations

import pytest

from core.mail_quota import DAILY_QUOTA
from core.models import EmailDelivery, User
from core.tasks import warn_email_quota
from notifications.models import Notification

pytestmark = pytest.mark.django_db


def _sent(provider: str, n: int) -> None:
    """`n` ta yuborilgan xat — hisoblagich shu qatorlardan o'qiydi."""
    EmailDelivery.objects.bulk_create(
        [
            EmailDelivery(
                to_email=f"u{i}@example.com",
                subject="s",
                provider=provider,
                status=EmailDelivery.Status.SENT,
            )
            for i in range(n)
        ]
    )


def _xodim(username: str = "xodim", **kw) -> User:
    return User.objects.create_user(username, password="x", is_staff=True, **kw)


def _ogohlantirishlar(user: User):
    return Notification.objects.filter(user=user, ref_type="mail_quota")


class TestOgohlantirish:
    def test_kvota_tugaganda_xodimga_xabar_boradi(self) -> None:
        xodim = _xodim()
        _sent("brevo", DAILY_QUOTA["brevo"])  # 300/300 — shift tugadi

        assert warn_email_quota() == "ok"

        xabar = _ogohlantirishlar(xodim).get()
        assert xabar.kind == Notification.Kind.SYSTEM
        assert "brevo" in xabar.body
        assert "tugadi" in xabar.body

    def test_kvota_tugamagan_bolsa_jim(self) -> None:
        """Shovqin qilmaslik — ogohlantirish faqat haqiqiy holatda."""
        xodim = _xodim()
        _sent("brevo", 10)  # 10/300 — 3%

        assert warn_email_quota() == "ok"

        assert not _ogohlantirishlar(xodim).exists()

    def test_80_foiz_chegarasida_xabar_boradi(self) -> None:
        """Chegara — `WARN_AT` (0.8). 240/300 = aynan 80%."""
        xodim = _xodim()
        _sent("brevo", 240)

        warn_email_quota()

        assert "80%" in _ogohlantirishlar(xodim).get().body

    def test_navbatdan_oshib_ketgan_xat_alohida_aytiladi(self) -> None:
        """Eng xavfli holat: navbat ham tugadi, xat YO'QOLADI."""
        xodim = _xodim()
        # brevo: 300 kvota + 1000 navbat = 1300 shift; 1350 — 50 tasi yo'q.
        _sent("brevo", 1350)

        warn_email_quota()

        body = _ogohlantirishlar(xodim).get().body
        assert "50 xat YETKAZILMAYDI" in body

    def test_bosh_jadval_hech_narsa_yozmaydi(self) -> None:
        """Kvota hisoblanmaydigan holat: jadval bo'sh — jim."""
        _xodim()

        assert warn_email_quota() == "ok"

        assert Notification.objects.count() == 0

    def test_faqat_kvotasi_bor_provayder_ogohlantiradi(self) -> None:
        """`console` kvotasiz (0), ya'ni u hech qachon ogohlantirmaydi.

        Salbiy test: agar `configured` sharti tushib qolsa, `console`
        qatori ham «tugadi» deb hisoblanib, har kuni yolg'on xabar
        kelardi.
        """
        xodim = _xodim()
        _sent("console", 50_000)

        assert warn_email_quota() == "ok"

        assert not _ogohlantirishlar(xodim).exists()

    def test_sarlavha_va_matn_bitta_manbadan(self) -> None:
        """Sarlavha ham, matn ham `mail_quota` dan — `tasks.py` da qattiq
        yozilgan matn qolmasligi kerak.

        Aks holda xabar ikki faylga bo'linadi: matnni o'zgartirgan odam
        sarlavhani topa olmaydi (va teskarisi).
        """
        from core import mail_quota

        xodim = _xodim()
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        xabar = _ogohlantirishlar(xodim).get()
        assert xabar.title == mail_quota.ALERT_TITLE
        assert xabar.body == mail_quota.summary()


class TestKimOladi:
    def test_xodim_bolmasa_otkazib_yuboriladi(self) -> None:
        """Xodim yo'q — yozadigan hech kim yo'q, lekin yiqilmaydi."""
        _sent("brevo", DAILY_QUOTA["brevo"])

        assert warn_email_quota() == "skipped"

    def test_oddiy_foydalanuvchi_xabar_olmaydi(self) -> None:
        """Bu ichki xabar: 1000 talik kampaniyada begona odam ko'rmasin."""
        xodim = _xodim()
        oddiy = User.objects.create_user("oddiy", password="x")
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        assert _ogohlantirishlar(xodim).exists()
        assert not _ogohlantirishlar(oddiy).exists()

    def test_faol_bolmagan_xodim_xabar_olmaydi(self) -> None:
        """Bloklangan xodimga yozish — ko'rilmaydigan navbat."""
        faol = _xodim("faol")
        _xodim("bloklangan", is_active=False)
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        assert Notification.objects.count() == 1
        assert Notification.objects.get().user_id == faol.pk

    def test_sozlamada_ochirilgan_bolsa_ham_keladi(self) -> None:
        """`notify_prefs` — hurmat qilinmaydi (ataylab chetlanish).

        `notify()` ishlatilsa bu test yiqilardi: xodim «system» turini
        o'chirib qo'ysa, kvota tugayotganini hech kim bilmasdi.
        """
        xodim = _xodim()
        xodim.notify_prefs = {"system": {"site": False, "telegram": False}}
        xodim.save(update_fields=["notify_prefs"])
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        assert _ogohlantirishlar(xodim).exists()

    def test_bir_nechta_xodimga_xabar_boradi(self) -> None:
        _xodim("birinchi")
        _xodim("ikkinchi")
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        assert Notification.objects.count() == 2


class TestTakrorlanmaslik:
    def test_bir_kunda_ikki_marta_yursa_ham_bitta_yozuv(self) -> None:
        """Beat soatiga bir marta yuradi — kuniga 24 ta xabar BO'LMASLIGI.

        `get_or_create` `ref_id` sifatida UTC kunni yozadi, ya'ni takror
        chaqiruv yangi qator ochmaydi.
        """
        xodim = _xodim()
        _sent("brevo", DAILY_QUOTA["brevo"])

        assert warn_email_quota() == "ok"
        assert warn_email_quota() == "ok"
        assert warn_email_quota() == "ok"

        assert _ogohlantirishlar(xodim).count() == 1

    def test_ikkinchi_yurish_matnni_yangilamaydi(self) -> None:
        """Birinchi xabar — o'sha ondagi holat; keyin o'zgarsa ham qoladi.

        Bu ataylab: raqam keyin o'zgarsa xabar «eski» bo'lib qolmaydi,
        chunki u o'sha paytdagi holatni yozib qo'ygan. Muhimi —
        takroriy yozuv yaratilmasin (yuqoridagi test).
        """
        xodim = _xodim()
        _sent("brevo", 240)  # 80% — ogohlantirish

        warn_email_quota()
        birinchi = _ogohlantirishlar(xodim).get().body

        _sent("brevo", 200)  # endi 440/300 — tugagan
        warn_email_quota()

        assert _ogohlantirishlar(xodim).get().body == birinchi

    def test_ref_id_utc_kun(self) -> None:
        """Kalit — kun sanasi, ya'ni ertaga YANGI xabar keladi."""
        from core import mail_quota

        xodim = _xodim()
        _sent("brevo", DAILY_QUOTA["brevo"])

        warn_email_quota()

        assert _ogohlantirishlar(xodim).get().ref_id == mail_quota.day_start().date().isoformat()


class TestXatogaChidamlilik:
    def test_yozish_yiqilsa_ham_vazifa_yiqilmaydi(self, monkeypatch) -> None:
        """Ogohlantirish hech narsani to'xtatmaydi — xato yutiladi.

        Muhim: ro'yxatdan o'tish oqimi bunga bog'liq emas, ya'ni bu
        yerdagi xato hech qachon foydalanuvchiga ko'rinmasligi kerak.
        """
        _xodim()
        _sent("brevo", DAILY_QUOTA["brevo"])

        def portla(*a, **kw):
            raise RuntimeError("baza yiqildi")

        monkeypatch.setattr(Notification.objects, "get_or_create", portla)

        assert warn_email_quota() == "ok"  # yiqilmadi

    def test_bitta_xodim_yiqilsa_qolganlari_xabar_oladi(self, monkeypatch) -> None:
        """Bitta qator xatosi qolgan xodimlarni chetlab o'tmasligi kerak."""
        birinchi = _xodim("birinchi")
        _xodim("ikkinchi")
        _sent("brevo", DAILY_QUOTA["brevo"])

        asl = Notification.objects.get_or_create

        def tanlab(user, **kw):
            if user.pk == birinchi.pk:
                raise RuntimeError("shu qator yiqildi")
            return asl(user=user, **kw)

        monkeypatch.setattr(Notification.objects, "get_or_create", tanlab)

        assert warn_email_quota() == "ok"
        assert Notification.objects.count() == 1
        assert Notification.objects.get().user.username == "ikkinchi"
