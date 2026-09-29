"""User.origin enum va backfill logikasi — WP3."""

from __future__ import annotations

import pytest
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.utils import timezone

from core.models import User


@pytest.mark.django_db
class TestUserOrigin:
    def test_origin_field_exists(self) -> None:
        """User modelida `origin` maydoni bor."""
        user = User.objects.create_user("origin_probe", password="x")
        assert hasattr(user, "origin")
        assert user.origin == User.Origin.REAL

    def test_enum_values(self) -> None:
        """Origin enum to'rt qiymatga ega."""
        assert User.Origin.REAL.value == "real"
        assert User.Origin.DEMO.value == "demo"
        assert User.Origin.IMPORTED.value == "imported"
        assert User.Origin.STAFF.value == "staff"

    def test_imported_is_separate_value(self) -> None:
        """`imported` alohida qiymat — demo bilan birga emas."""
        assert User.Origin.IMPORTED.value != User.Origin.DEMO.value
        assert User.Origin.IMPORTED.value != User.Origin.REAL.value
        assert User.Origin.IMPORTED.value != User.Origin.STAFF.value

    def test_default_value_is_real(self) -> None:
        """Yangi foydalanuvchi sukut bo'yicha `real`."""
        user = User.objects.create_user("real_default", password="x")
        assert user.origin == "real"

    def test_attempt_origin_is_absent(self) -> None:
        """Attempt.origin YO'Q — D9 rad etgan."""
        from judging.models import Attempt

        assert not hasattr(Attempt, "origin")


@pytest.mark.django_db
class TestBackfillOrigin:
    def test_backfill_audit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Backfill har bir tur uchun to'g'ri hisoblaydi.

        ⚠️ `call_command(stdout=...)` parametri faqat oqimni ALMASHTIRADI;
        pytest'da chiqishni `capsys.readouterr()` bilan o'qiladi. Ilgari
        `capsys.stdout` yozilgandi — bunday atribut yo'q va test
        yiqilardi (QA 2026-09-29 da o'lchandi).
        """
        # Demo foydalanuvchilar — seed_stress bilan bir xil naqsh:
        # prefiks + ishlatib bo'ladigan parol. Email domeni ATAYLAB oddiy
        # (`@rankwant.uz`): 2026-09-29 QA da aniqlandiki, demo markeri
        # faqat PREFIKS — email domeniga tayanadigan hech narsa yo'q.
        demo1 = User.objects.create_user("neytron_000001", email="demo1@rankwant.uz", password="x")
        demo2 = User.objects.create_user("stress_000001", email="demo2@rankwant.uz", password="x")
        # Prefikssiz seed — demo EMAS (yangi qoida: demo markeri faqat
        # prefiks). `regular_seed` ataylab: u oldin @example.invalid orqali
        # demo bo'lar edi, endi REAL — bu o'zgarish testda qayd etiladi.
        seeded_regular = User.objects.create_user(
            "regular_seed", email="seed@rankwant.uz", password="x"
        )

        # Imported foydalanuvchilar
        imported1 = User.objects.create_user("cf_imported_1", email="", password="")
        imported1.password = make_password(None)
        imported1.terms_accepted_at = None
        imported1.save()

        # Staff foydalanuvchi
        staff = User.objects.create_user(
            "staffer", email="staff@rankwant.uz", password="x", is_staff=True
        )

        # Superuser
        superuser = User.objects.create_user(
            "boss", email="boss@rankwant.uz", password="x", is_superuser=True
        )

        # Real foydalanuvchi
        real = User.objects.create_user(
            "azizbek",
            email="aziz@example.com",
            password="x",
            terms_accepted_at=timezone.now(),
        )

        # Oldingi origin'larni tozalash (real sukut)
        for u in (demo1, demo2, seeded_regular, imported1, staff, superuser, real):
            User.objects.filter(pk=u.pk).update(origin="real")

        call_command("backfill_origin")
        captured = capsys.readouterr()

        # Audit count chiqishi kerak
        assert "real=" in captured.out
        assert "demo=" in captured.out
        assert "imported=" in captured.out
        assert "staff=" in captured.out
        assert "total=" in captured.out

        # Tekshirish
        demo1.refresh_from_db()
        demo2.refresh_from_db()
        seeded_regular.refresh_from_db()
        imported1.refresh_from_db()
        staff.refresh_from_db()
        superuser.refresh_from_db()
        real.refresh_from_db()

        assert demo1.origin == User.Origin.DEMO
        assert demo2.origin == User.Origin.DEMO
        # Prefikssiz seed — REAL (email domen qoidasi olib tashlandi:
        # 2026-09-29 QA — demo markeri faqat username prefiksi)
        assert seeded_regular.origin == User.Origin.REAL
        assert imported1.origin == User.Origin.IMPORTED
        assert staff.origin == User.Origin.STAFF
        assert superuser.origin == User.Origin.STAFF
        assert real.origin == User.Origin.REAL

    def test_backfill_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        """dry-run hech narsa o'zgartirmaydi."""
        user = User.objects.create_user("neytron_dry", email="dry@rankwant.uz", password="x")
        user.origin = User.Origin.REAL
        user.save()

        call_command("backfill_origin", "--dry-run")
        captured = capsys.readouterr()
        assert "dry-run" in captured.out

        user.refresh_from_db()
        assert user.origin == User.Origin.REAL
