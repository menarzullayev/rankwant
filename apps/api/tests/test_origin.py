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
        assert User.Origin.REAL == "real"
        assert User.Origin.DEMO == "demo"
        assert User.Origin.IMPORTED == "imported"
        assert User.Origin.STAFF == "staff"

    def test_imported_is_separate_value(self) -> None:
        """`imported` alohida qiymat — demo bilan birga emas."""
        assert User.Origin.IMPORTED != User.Origin.DEMO
        assert User.Origin.IMPORTED != User.Origin.REAL
        assert User.Origin.IMPORTED != User.Origin.STAFF

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
    def test_backfill_audit(self, capsys) -> None:
        """Backfill har bir tur uchun to'g'ri hisoblaydi."""
        # Demo foydalanuvchilar
        demo1 = User.objects.create_user(
            "neytron_000001", email="demo1@example.invalid", password="x"
        )
        demo2 = User.objects.create_user(
            "stress_000001", email="demo2@example.com", password="x"
        )
        demo3 = User.objects.create_user(
            "regular_seed", email="seed@example.invalid", password="x"
        )

        # Imported foydalanuvchilar
        imported1 = User.objects.create_user(
            "cf_imported_1", email="", password=""
        )
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
        User.objects.filter(pk=demo1.pk).update(origin="real")
        User.objects.filter(pk=demo2.pk).update(origin="real")
        User.objects.filter(pk=demo3.pk).update(origin="real")
        User.objects.filter(pk=imported1.pk).update(origin="real")
        User.objects.filter(pk=staff.pk).update(origin="real")
        User.objects.filter(pk=superuser.pk).update(origin="real")
        User.objects.filter(pk=real.pk).update(origin="real")

        call_command("backfill_origin", stdout=capsys.stdout, stderr=capsys.stderr)
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
        demo3.refresh_from_db()
        imported1.refresh_from_db()
        staff.refresh_from_db()
        superuser.refresh_from_db()
        real.refresh_from_db()

        assert demo1.origin == User.Origin.DEMO
        assert demo2.origin == User.Origin.DEMO
        assert demo3.origin == User.Origin.DEMO
        assert imported1.origin == User.Origin.IMPORTED
        assert staff.origin == User.Origin.STAFF
        assert superuser.origin == User.Origin.STAFF
        assert real.origin == User.Origin.REAL

    def test_backfill_dry_run(self, capsys) -> None:
        """dry-run hech narsa o'zgartirmaydi."""
        user = User.objects.create_user(
            "neytron_dry", email="dry@example.invalid", password="x"
        )
        user.origin = User.Origin.REAL
        user.save()

        call_command("backfill_origin", "--dry-run", stdout=capsys.stdout)
        user.refresh_from_db()
        assert user.origin == User.Origin.REAL
