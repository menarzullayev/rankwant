"""Profil 3-bosqichi — sertifikat, murabbiy, obunachilar, ijtimoiy havolalar,
tuman va maktab katalogi (ADR-0017, ADR-0019)."""

from __future__ import annotations

import hashlib
import hmac
import io
import re
import time
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from classroom.models import Classroom, ClassroomMember
from contests.certificates import issue
from contests.models import Certificate, Contest, Standing
from core import oauth
from core.models import School, SocialAccount, User, UserSession
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Language, Problem
from profiles import external
from profiles.catalog import UZ_DISTRICTS
from profiles.models import ExternalProfile, Follow

ROOT = Path(__file__).resolve().parents[3]


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def profil(user: User, viewer: User | None = None) -> Any:
    client = kirgan(viewer) if viewer else APIClient()
    return client.get(reverse("user-profile", args=[user.username])).data


def test_tuman_kodlari_web_katalogi_bilan_bir_xil() -> None:
    source = (ROOT / "apps/web/src/lib/regions.ts").read_text(encoding="utf-8")
    web: dict[str, list[str]] = {}
    for code, region in re.findall(r'\["([a-z0-9-]+)", "([a-z-]+)", "(?:t|sh)"', source):
        web.setdefault(region, []).append(code)

    assert web == {region: list(codes) for region, codes in UZ_DISTRICTS.items()}
    assert sum(len(codes) for codes in UZ_DISTRICTS.values()) >= 200


@pytest.mark.django_db
class TestJoylashuv:
    def test_tuman_faqat_viloyat_ichidan(self, user: User) -> None:
        client = kirgan(user)
        me = reverse("me")

        ok = client.patch(
            me,
            {"country": "UZ", "region": "toshkent-shahri", "district": "chilonzor"},
            format="json",
        )
        wrong = client.patch(me, {"district": "nukus"}, format="json")
        moved = client.patch(me, {"region": "andijon"}, format="json")

        assert ok.status_code == 200
        assert wrong.status_code == 400
        assert moved.status_code == 200
        user.refresh_from_db()
        assert (user.region, user.district) == ("andijon", ""), "eski tuman tozalandi"

    def test_boshqa_mamlakatda_shahar(self, user: User) -> None:
        client = kirgan(user)
        client.patch(
            reverse("me"),
            {"country": "KZ", "city": "Almaty", "district": "chilonzor"},
            format="json",
        )

        user.refresh_from_db()
        assert (user.city, user.district) == ("Almaty", "")
        assert profil(user)["info"]["city"] == "Almaty"


@pytest.mark.django_db
class TestMaktabKatalogi:
    def test_qidiruv_tanlash_va_reyting(self, user: User, other_user: User) -> None:
        school = School.objects.create(name="Toshkent 1-maktab", region="toshkent-shahri")
        closed = School.objects.create(name="Toshkent yopiq maktab", is_active=False)
        client = kirgan(user)

        found = APIClient().get(reverse("school-list"), {"q": "toshkent"}).data
        chosen = client.patch(reverse("me"), {"school_ref": school.pk}, format="json")
        refused = client.patch(reverse("me"), {"school_ref": closed.pk}, format="json")
        leaders = APIClient().get(reverse("user-list"), {"school": school.pk}).data

        assert [row["name"] for row in found["results"]] == ["Toshkent 1-maktab"]
        assert chosen.status_code == 200
        assert refused.status_code == 400
        assert [row["username"] for row in leaders["results"]] == ["aziz"]
        info = profil(user)["info"]
        assert (info["school"], info["school_id"]) == ("Toshkent 1-maktab", str(school.pk))
        assert APIClient().get(reverse("school-detail", args=[school.pk])).data["members"] == 1


@pytest.mark.django_db
class TestMurabbiy:
    def test_auditoriya_egasidan_va_yashiriladi(self, user: User, other_user: User) -> None:
        room = Classroom.objects.create(name="A", slug="a", owner=other_user, join_code="X1")
        ClassroomMember.objects.create(classroom=room, user=user)

        assert [row["username"] for row in profil(user)["coach"]] == ["bekzod"]
        assert profil(other_user)["coach"] == [], "yordamchi yoki egasi o'quvchi emas"

        user.hidden_fields = ["email", "coach"]
        user.save(update_fields=["hidden_fields"])
        assert profil(user, other_user)["coach"] == []
        assert profil(user, user)["coach"][0]["username"] == "bekzod"


@pytest.mark.django_db
class TestObunachilar:
    def test_qidiruv_saralash_va_maxfiylik(self, user: User, other_user: User) -> None:
        zafar = User.objects.create_user(username="zafar", password="Parol!12345")
        other_user.rating_contest, other_user.school = 1500, "5-maktab"
        other_user.save(update_fields=["rating_contest", "school"])
        zafar.rating_contest, zafar.school = 1900, "7-maktab"
        zafar.hidden_fields = ["email", "online", "school"]
        zafar.save(update_fields=["rating_contest", "school", "hidden_fields"])
        for person in (other_user, zafar):
            Follow.objects.create(follower=person, following=user)
            UserSession.objects.create(user=person, session_key=person.username.ljust(40, "x"))
        url = reverse("user-followers", args=[user.username])

        found = APIClient().get(url, {"q": "bek"}).data["results"]
        by_rating = APIClient().get(url, {"ordering": "rating"}).data["results"]

        assert [row["username"] for row in found] == ["bekzod"]
        assert [row["username"] for row in by_rating] == ["zafar", "bekzod"]
        rows = {row["username"]: row for row in by_rating}
        assert (rows["bekzod"]["school"], rows["bekzod"]["rating_contest"]) == ("5-maktab", 1500)
        assert rows["bekzod"]["last_seen"] is not None
        assert (rows["zafar"]["school"], rows["zafar"]["last_seen"]) == ("", None)


@pytest.mark.django_db
class TestIjtimoiyHavolalar:
    def test_havola_normallashadi(self) -> None:
        assert external.normalize("telegram", "https://t.me/aziz_dev?start=1") == "aziz_dev"
        assert external.normalize("youtube", "https://youtube.com/@AzizDev") == "AzizDev"
        assert external.normalize("x", "@aziz") == "aziz"
        assert external.normalize("blog", "https://aziz.dev/blog") == "https://aziz.dev/blog"
        for kind, value in (("blog", "http://aziz.dev"), ("github", "-yomon"), ("telegram", "ab")):
            with pytest.raises(ValueError):
                external.normalize(kind, value)

    def test_ulangan_hisobdan_taxallus(self, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
        SocialAccount.objects.create(user=user, provider="telegram", uid="7", username="aziz_tg")
        SocialAccount.objects.create(user=user, provider="github", uid="42")
        calls: list[str] = []

        def fake_json(url: str, *args: Any, **kwargs: Any) -> Any:
            calls.append(url)
            return {"login": "azizgh"}

        monkeypatch.setattr(external, "_json", fake_json)

        body = kirgan(user).get(reverse("me-external-connected")).data
        again = kirgan(user).get(reverse("me-external-connected")).data

        assert body == again == {"telegram": "aziz_tg", "github": "azizgh"}
        assert calls == ["https://api.github.com/user/42"], "bir marta so'raladi, keyin saqlangan"

    def test_telegram_taxallusi_kirishda_olinadi(self, settings: Any) -> None:
        settings.TELEGRAM_BOT_TOKEN = "123:abc"
        payload = {"id": "7", "username": "aziz_tg", "auth_date": str(int(time.time()))}
        check = "\n".join(f"{key}={payload[key]}" for key in sorted(payload))
        secret = hashlib.sha256(b"123:abc").digest()
        payload["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()

        assert oauth.telegram_identity(payload).handle == "aziz_tg"

    def test_ijtimoiy_havolalar_yashiriladi(self, user: User, other_user: User) -> None:
        ExternalProfile.objects.create(user=user, kind="github", handle="aziz")
        user.hidden_fields = ["email", "social"]
        user.save(update_fields=["hidden_fields"])

        assert profil(user, other_user)["external"] == []
        assert profil(user, user)["external"][0]["handle"] == "aziz"


def ishtirokchilar(contest: Contest, problem: Problem, language: Language, n: int) -> list[User]:
    """`n` ishtirokchi: har biri musobaqa oynasida bitta urinish bilan."""
    users = [User.objects.create_user(username=f"u{i:02d}", password="x") for i in range(n)]
    for i, person in enumerate(users):
        Standing.objects.create(
            contest=contest, user=person, rank=i + 1, solved_count=max(0, 5 - i // 8), penalty=i
        )
        Attempt.objects.create(
            user=person,
            problem=problem,
            language=language,
            source_code="x",
            verdict=Verdict.AC,
            contest=contest,
        )
    Attempt.objects.filter(contest=contest).update(
        created_at=contest.start_at + timedelta(minutes=5)
    )
    return users


@pytest.mark.django_db
class TestSertifikatlar:
    def test_darajalar_va_teng_orin(
        self, contest: Contest, problem: Problem, language: Language
    ) -> None:
        users = ishtirokchilar(contest, problem, language, 40)
        # 2 va 3-o'rin teng: ikkalasi kumush, keyingisi 4-o'rin — bronza yo'q.
        Standing.objects.filter(user=users[2]).update(solved_count=5, penalty=1)
        User.objects.create_user(username="kirmagan", password="x")

        assert issue(contest) == 40
        assert issue(contest) == 40, "takroriy chaqiruv xavfsiz"

        certs = {c.user.username: c for c in Certificate.objects.select_related("user")}
        assert len(certs) == 40
        assert [(certs[f"u{i:02d}"].place, certs[f"u{i:02d}"].tier) for i in range(5)] == [
            (1, "gold"),
            (2, "silver"),
            (2, "silver"),
            (4, "top10"),
            (5, "participant"),
        ]
        assert certs["u00"].participants == 40

    def test_virtual_va_yopiq_musobaqada_yoq(
        self, contest: Contest, problem: Problem, language: Language
    ) -> None:
        ishtirokchilar(contest, problem, language, 3)
        Contest.objects.filter(pk=contest.pk).update(is_virtual=True)
        contest.refresh_from_db()

        assert issue(contest) == 0

    def test_tekshirish_pdf_va_royxat(
        self, contest: Contest, problem: Problem, language: Language
    ) -> None:
        winner = ishtirokchilar(contest, problem, language, 3)[0]
        issue(contest)
        cert = Certificate.objects.get(user=winner)

        body = APIClient().get(reverse("certificate", args=[cert.pk])).data
        pdf = APIClient().get(reverse("certificate-pdf", args=[cert.pk]))
        mine = APIClient().get(reverse("user-certificates", args=[winner.username])).data

        assert (body["username"], body["place"], body["tier"]) == ("u00", 1, "gold")
        assert body["contest"]["slug"] == contest.slug
        assert pdf.status_code == 200 and pdf["Content-Type"] == "application/pdf"
        assert pdf.content.startswith(b"%PDF")
        assert [row["id"] for row in mine["results"]] == [str(cert.pk)]
        assert APIClient().get(reverse("certificate", args=[uuid.uuid4()])).status_code == 404

        winner.is_active = False
        winner.save(update_fields=["is_active"])
        assert APIClient().get(reverse("certificate", args=[cert.pk])).status_code == 404

    def test_buyruq_yakunlanganlarni_toldiradi(
        self, contest: Contest, problem: Problem, language: Language
    ) -> None:
        ishtirokchilar(contest, problem, language, 2)
        Contest.objects.filter(pk=contest.pk).update(ratings_applied_at=timezone.now())
        out = io.StringIO()

        call_command("issue_certificates", stdout=out)

        assert Certificate.objects.count() == 2


@pytest.mark.django_db
def test_finalize_sertifikat_beradi(contest: Contest, problem: Problem, language: Language) -> None:
    from contests.services import finalize_contest

    ishtirokchilar(contest, problem, language, 3)

    finalize_contest(contest)

    assert Certificate.objects.filter(contest=contest).count() == 3
