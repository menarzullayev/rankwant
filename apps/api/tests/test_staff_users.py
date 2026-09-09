"""Staff API — foydalanuvchilar boshqaruvi (admin UI)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from notifications.models import Notification
from qvant import ledger
from qvant.models import QvantTransaction


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def superuser(db) -> User:
    return User.objects.create_superuser("root", password="x")


def as_user(u: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=u)
    return c


def detail(username: str) -> str:
    return reverse("staff-user-detail", args=[username])


@pytest.mark.django_db
class TestAccess:
    def test_anonim(self, user) -> None:
        assert APIClient().get(reverse("staff-user-list")).status_code in (401, 403)

    def test_oddiy_foydalanuvchi(self, user, other_user) -> None:
        c = as_user(user)
        assert c.get(reverse("staff-user-list")).status_code == 403
        assert c.patch(detail(other_user.username), {"bio": "x"}).status_code == 403
        assert c.post(reverse("staff-user-broadcast"), {"title": "x"}).status_code == 403

    def test_ommaviy_api_email_bermaydi(self, user) -> None:
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert "email" not in body and "is_active" not in body


@pytest.mark.django_db
class TestCrud:
    def test_royxat_va_qidiruv(self, staff, user, other_user) -> None:
        user.email = "aziz@example.uz"
        user.save(update_fields=["email"])
        c = as_user(staff)
        body = c.get(reverse("staff-user-list")).json()
        assert body["count"] == 3
        assert "email" in body["results"][0]

        for q in ("azi", "aziz@example"):
            found = c.get(reverse("staff-user-list"), {"search": q}).json()["results"]
            assert [u["username"] for u in found] == [user.username]

    def test_tartiblash(self, staff, user, other_user) -> None:
        other_user.rating_skills = 500
        other_user.save(update_fields=["rating_skills"])
        rows = as_user(staff).get(reverse("staff-user-list"), {"ordering": "-rating_skills"}).json()
        assert rows["results"][0]["username"] == other_user.username

    def test_olish_qvant_balansi_bilan(self, staff, user) -> None:
        ledger.credit(user, 40, QvantTransaction.Reason.STREAK)
        body = as_user(staff).get(detail(user.username)).json()
        assert body["qvant_balance"] == 40
        assert body["is_superuser"] is False

    def test_tahrirlash(self, staff, user) -> None:
        r = as_user(staff).patch(
            detail(user.username),
            {"display_name": "Aziz A.", "bio": "salom", "is_active": False},
        )
        assert r.status_code == 200, r.json()
        user.refresh_from_db()
        assert (user.display_name, user.bio, user.is_active) == ("Aziz A.", "salom", False)

    def test_faqat_ruxsat_etilgan_maydonlar(self, staff, user) -> None:
        """username/email/reyting/parol read-only — jimgina e'tiborsiz qoldiriladi."""
        old_hash = user.password
        r = as_user(staff).patch(
            detail(user.username),
            {"username": "boshqa", "email": "x@y.z", "rating_skills": 9000, "password": "yangi"},
        )
        assert r.status_code == 200
        user.refresh_from_db()
        assert user.username == "aziz"
        assert user.email == ""
        assert user.rating_skills == 0
        assert user.password == old_hash

    def test_yaratish_va_ochirish_yoq(self, staff, user) -> None:
        c = as_user(staff)
        assert c.post(reverse("staff-user-list"), {"username": "yangi"}).status_code == 405
        assert c.delete(detail(user.username)).status_code == 405
        assert User.objects.filter(username=user.username).exists()


@pytest.mark.django_db
class TestStaffGuards:
    def test_ozini_bloklay_olmaydi(self, staff) -> None:
        r = as_user(staff).patch(detail(staff.username), {"is_active": False})
        assert r.status_code == 400
        assert "is_active" in r.json()["error"]["details"]
        staff.refresh_from_db()
        assert staff.is_active

    def test_ozini_xodimlikdan_chiqara_olmaydi(self, superuser) -> None:
        # Superuser ham — qoida hamma uchun bir xil
        r = as_user(superuser).patch(detail(superuser.username), {"is_staff": False})
        assert r.status_code == 400
        assert "is_staff" in r.json()["error"]["details"]
        superuser.refresh_from_db()
        assert superuser.is_staff

    def test_oz_profilini_tahrirlash_mumkin(self, staff) -> None:
        """Forma barcha maydonlarni yuboradi — o'zgarmagan qiymat xato emas."""
        r = as_user(staff).patch(
            detail(staff.username), {"display_name": "Men", "is_active": True, "is_staff": True}
        )
        assert r.status_code == 200, r.json()

    def test_is_staff_faqat_superuser(self, staff, superuser, user) -> None:
        r = as_user(staff).patch(detail(user.username), {"is_staff": True})
        assert r.status_code == 400
        assert "is_staff" in r.json()["error"]["details"]
        user.refresh_from_db()
        assert not user.is_staff

        r = as_user(superuser).patch(detail(user.username), {"is_staff": True})
        assert r.status_code == 200
        user.refresh_from_db()
        assert user.is_staff

    def test_oddiy_xodim_ozgarmagan_is_staff_yuborishi_mumkin(self, staff, user) -> None:
        r = as_user(staff).patch(detail(user.username), {"is_staff": False, "bio": "x"})
        assert r.status_code == 200


@pytest.mark.django_db
class TestQvant:
    def test_kredit_shiftsiz(self, staff, user) -> None:
        r = as_user(staff).post(
            reverse("staff-user-qvant", args=[user.username]),
            {"amount": 500, "note": "Musobaqa g'olibi uchun sovrin"},
        )
        assert r.status_code == 200, r.json()
        assert r.json() == {"amount": 500, "balance": 500}
        tx = QvantTransaction.objects.get(user=user)
        assert tx.reason == QvantTransaction.Reason.ADMIN
        assert (tx.ref_type, tx.ref_id) == ("admin", "Musobaqa g'olibi uchun sovrin")
        assert ledger.get_wallet(user).balance == 500

    def test_debit(self, staff, user) -> None:
        ledger.credit(user, 50, QvantTransaction.Reason.STREAK)
        r = as_user(staff).post(
            reverse("staff-user-qvant", args=[user.username]), {"amount": -20, "note": "jarima"}
        )
        assert r.status_code == 200
        assert r.json() == {"amount": -20, "balance": 30}

    def test_balans_yetmasa_400(self, staff, user) -> None:
        r = as_user(staff).post(
            reverse("staff-user-qvant", args=[user.username]), {"amount": -20, "note": "jarima"}
        )
        assert r.status_code == 400
        assert "amount" in r.json()["error"]["details"]
        assert not QvantTransaction.objects.filter(user=user).exists()

    def test_nol_va_izohsiz_rad(self, staff, user) -> None:
        c = as_user(staff)
        url = reverse("staff-user-qvant", args=[user.username])
        assert c.post(url, {"amount": 0, "note": "x"}).status_code == 400
        assert c.post(url, {"amount": 5}).status_code == 400

    def test_uzun_izoh_qisqartiriladi(self, staff, user) -> None:
        r = as_user(staff).post(
            reverse("staff-user-qvant", args=[user.username]), {"amount": 1, "note": "a" * 100}
        )
        assert r.status_code == 200
        assert QvantTransaction.objects.get(user=user).ref_id == "a" * 64


@pytest.mark.django_db
class TestNotify:
    def test_bitta(self, staff, user, other_user) -> None:
        r = as_user(staff).post(
            reverse("staff-user-notify", args=[user.username]),
            {"title": "Salom", "body": "Xush kelibsiz"},
        )
        assert r.status_code == 201
        n = Notification.objects.get(pk=r.json()["id"])
        assert (n.user, n.kind, n.title, n.body) == (user, "system", "Salom", "Xush kelibsiz")
        assert not Notification.objects.filter(user=other_user).exists()

    def test_sarlavhasiz_rad(self, staff, user) -> None:
        r = as_user(staff).post(reverse("staff-user-notify", args=[user.username]), {"body": "x"})
        assert r.status_code == 400

    def test_broadcast_faqat_faollarga(self, staff, user, other_user) -> None:
        other_user.is_active = False
        other_user.save(update_fields=["is_active"])
        r = as_user(staff).post(reverse("staff-user-broadcast"), {"title": "E'lon"})
        assert r.status_code == 201
        assert r.json() == {"count": 2}  # staff + user
        assert set(Notification.objects.values_list("user__username", flat=True)) == {
            staff.username,
            user.username,
        }
        assert Notification.objects.filter(kind=Notification.Kind.SYSTEM).count() == 2


@pytest.mark.django_db
class TestPrivilegedTargets:
    """Oddiy xodim imtiyozli hisoblarni bloklay olmaydi — superuser esa oladi."""

    def test_xodim_superuserni_bloklay_olmaydi(self, staff, superuser) -> None:
        r = as_user(staff).patch(detail(superuser.username), {"is_active": False}, format="json")
        assert r.status_code == 400
        superuser.refresh_from_db()
        assert superuser.is_active

    def test_xodim_boshqa_xodimni_bloklay_olmaydi(self, staff, db) -> None:
        other = User.objects.create_user("staff_b", password="x", is_staff=True)
        r = as_user(staff).patch(detail(other.username), {"is_active": False}, format="json")
        assert r.status_code == 400

    def test_superuser_xodimni_bloklaydi(self, superuser, staff) -> None:
        r = as_user(superuser).patch(detail(staff.username), {"is_active": False}, format="json")
        assert r.status_code == 200
        staff.refresh_from_db()
        assert not staff.is_active

    def test_xodim_oddiy_foydalanuvchini_bloklaydi(self, staff, user) -> None:
        """Cheklov faqat imtiyozli hisoblar uchun — oddiy ban ishlayveradi."""
        r = as_user(staff).patch(detail(user.username), {"is_active": False}, format="json")
        assert r.status_code == 200


@pytest.mark.django_db
class TestPruneTestUsers:
    """Stress sinovi minglab hisob yaratadi — ularni tozalash yo'li kerak."""

    def prune(self, **kwargs):
        from django.core.management import call_command

        call_command("prune_test_users", **kwargs)

    def test_prefiksdagilar_ochiriladi(self) -> None:
        from core.models import User

        User.objects.create_user("e2e_1")
        User.objects.create_user("e2e_2")
        haqiqiy = User.objects.create_user("aziz")

        self.prune(prefix="e2e")

        assert list(User.objects.values_list("username", flat=True)) == [haqiqiy.username]

    def test_xodim_hech_qachon_ochirilmaydi(self) -> None:
        """Nomi mos kelib qolgan admin bilan kirish huquqi ham ketardi."""
        from core.models import User

        User.objects.create_user("e2e_admin", is_staff=True)
        User.objects.create_user("e2e_oddiy")

        self.prune(prefix="e2e")

        assert list(User.objects.values_list("username", flat=True)) == ["e2e_admin"]

    def test_qisqa_prefiks_rad_etiladi(self) -> None:
        from django.core.management.base import CommandError

        with pytest.raises(CommandError):
            self.prune(prefix="e")

    def test_dry_run_ochirmaydi(self) -> None:
        from core.models import User

        User.objects.create_user("e2e_1")

        self.prune(prefix="e2e", dry_run=True)

        assert User.objects.filter(username="e2e_1").exists()


@pytest.mark.django_db
class TestSeedStress:
    """10 000 neytron — reyting va sahifalash haqiqiy yuk ostida sinaladi."""

    def seed(self, **kwargs):
        from django.core.management import call_command

        call_command("seed_stress", **kwargs)

    def test_yaratiladi_va_reytinglar_har_xil(self) -> None:
        self.seed(users=50, seed=1)

        rows = User.objects.filter(username__startswith="neytron_")
        assert rows.count() == 50
        assert rows.filter(username="neytron_000001").exists()
        # Bir xil reyting saralash yukini soxta qilardi.
        assert len(set(rows.values_list("rating_skills", flat=True))) > 10

    def test_parolsiz_hisob_kira_olmaydi(self) -> None:
        self.seed(users=3)

        assert User.objects.get(username="neytron_000001").has_usable_password() is False

    def test_parol_berilsa_kirish_mumkin(self) -> None:
        self.seed(users=3, password="Sinov!12345")

        assert User.objects.get(username="neytron_000002").check_password("Sinov!12345")

    def test_qayta_yuritish_takrorlamaydi(self) -> None:
        self.seed(users=5, seed=1)
        self.seed(users=8, seed=1)

        assert User.objects.filter(username__startswith="neytron_").count() == 8

    def test_prune_neytronlarni_ham_oladi(self) -> None:
        from django.core.management import call_command

        self.seed(users=5)
        call_command("prune_test_users", prefix="neytron")

        assert User.objects.filter(username__startswith="neytron_").count() == 0

    def test_urinishlar_va_yechilganlar_yoziladi(self, problem, language) -> None:
        from judging.models import Attempt
        from problems.models import TestCase as ProblemTest
        from ratings.models import UserSolvedProblem

        ProblemTest.objects.create(
            problem=problem, order=1, input_ref="s3://a/1.in", output_ref="s3://a/1.out"
        )

        self.seed(users=20, attempts=5, seed=7)

        assert Attempt.objects.count() > 0
        # `bulk_create` `save()` ni chetlab o'tadi — hajm nolda qolmasin.
        assert Attempt.objects.filter(source_size=0).count() == 0
        assert UserSolvedProblem.objects.count() > 0

        problem.refresh_from_db()
        assert problem.attempt_count == Attempt.objects.filter(problem=problem).count()
        assert (
            problem.solved_count
            == Attempt.objects.filter(problem=problem, verdict="AC")
            .values("user")
            .distinct()
            .count()
        )
