"""Profil — ko'nikma, karyera, tashqi profil, obuna, jamoa, kosmetika va
bildirishnoma kanallari."""

from __future__ import annotations

import urllib.error
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core import account
from core.models import SocialAccount, User
from notifications import services as notify_services
from notifications.models import Notification
from notifications.tasks import send_telegram
from profiles import external, teams
from profiles.models import ExternalProfile, Follow, Skill, Team, TeamMember, UserSkill
from qvant.models import ShopItem, UserInventory


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture(autouse=True)
def navbat(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, ...]]:
    """Tashqi reyting va Telegram vazifalari navbatga ketmaydi — yig'iladi.

    `.delay` almashtiriladi, `core.tasks.queue` EMAS: `queue` boshqa
    modullarga nomi bilan import qilingan, va birinchi import shu
    almashtirish paytiga to'g'ri kelsa soxta funksiya o'sha modulda
    butunlay qolib, keyingi test fayllarini buzardi (o'lchandi).
    """
    chaqiruvlar: list[tuple[Any, ...]] = []

    def yig(name: str) -> Any:
        def delay(*args: Any) -> None:
            chaqiruvlar.append((name, *args))

        return delay

    monkeypatch.setattr("profiles.tasks.refresh_external.delay", yig("profiles.refresh_external"))
    monkeypatch.setattr(
        "notifications.tasks.send_telegram.delay", yig("notifications.send_telegram")
    )
    return chaqiruvlar


@pytest.fixture
def skill(db: None) -> Skill:
    return Skill.objects.get_or_create(slug="greedy", defaults={"name_uz": "Ochko'z"})[0]


@pytest.mark.django_db
class TestKonikmaVaKaryera:
    def test_katalog_ochiq(self, skill: Skill) -> None:
        r = APIClient().get(reverse("skill-catalog"))

        assert r.status_code == 200
        assert "greedy" in {row["slug"] for row in r.data}

    def test_royxat_butunlay_almashtiriladi(self, user: User, skill: Skill) -> None:
        Skill.objects.create(slug="dp-sinov", name_uz="DP")
        c = kirgan(user)

        r = c.put(
            reverse("me-skills"),
            [{"skill": "greedy", "level": 80}, {"skill": "dp-sinov", "level": 40}],
            format="json",
        )
        assert [(row["skill"], row["level"]) for row in r.data] == [
            ("greedy", 80),
            ("dp-sinov", 40),
        ]

        r = c.put(reverse("me-skills"), [{"skill": "dp-sinov", "level": 55}], format="json")
        assert [(row["skill"], row["level"]) for row in r.data] == [("dp-sinov", 55)]

    @pytest.mark.parametrize(
        "body",
        [
            [{"skill": "greedy", "level": 101}],
            [{"skill": "uchish", "level": 10}],
            [{"skill": "greedy", "level": 1}, {"skill": "greedy", "level": 2}],
        ],
        ids=["100-dan-oshgan", "nomalum", "takror"],
    )
    def test_notogri_royxat_rad(self, user: User, skill: Skill, body: list[Any]) -> None:
        assert kirgan(user).put(reverse("me-skills"), body, format="json").status_code == 400
        assert not UserSkill.objects.filter(user=user).exists()

    def test_texnologiyalar_katalogdan(self, user: User) -> None:
        c = kirgan(user)

        r = c.put(reverse("me-technologies"), ["python", "cplusplus"], format="json")

        assert [row["slug"] for row in r.data] == ["python", "cplusplus"]
        assert c.put(reverse("me-technologies"), ["cobol-9000"], format="json").status_code == 400

    def test_talim_yillari_tekshiriladi(self, user: User) -> None:
        c = kirgan(user)
        togri = [
            {"organization": "TATU", "degree": "Bakalavr", "start_year": 2020, "end_year": 2024}
        ]
        teskari = [{"organization": "TATU", "start_year": 2024, "end_year": 2020}]

        assert c.put(reverse("me-educations"), togri, format="json").status_code == 200
        assert c.put(reverse("me-educations"), teskari, format="json").status_code == 400

    def test_ish_tajribasi_hozirgacha(self, user: User) -> None:
        r = kirgan(user).put(
            reverse("me-work"),
            [{"company": "EPAM", "title": "Backend", "start_year": 2022}],
            format="json",
        )

        assert r.status_code == 200
        assert r.data[0]["end_year"] is None


@pytest.mark.django_db
class TestTashqiProfil:
    def test_havoladan_handle_ajratiladi(self) -> None:
        assert external.normalize("codeforces", "https://codeforces.com/profile/tourist/") == (
            "tourist"
        )
        with pytest.raises(ValueError):
            external.normalize("atcoder", "yomon handle!")
        with pytest.raises(ValueError):
            external.normalize("linkedin", "https://kuzatuv.example/in/ali")

    def test_saqlanganda_reyting_navbatga_qoyiladi(
        self,
        user: User,
        navbat: list[tuple[Any, ...]],
        django_capture_on_commit_callbacks: Any,
    ) -> None:
        with django_capture_on_commit_callbacks(execute=True):
            r = kirgan(user).put(
                reverse("me-external"),
                [
                    {"kind": "codeforces", "handle": "tourist"},
                    {"kind": "linkedin", "handle": "https://linkedin.com/in/ali"},
                ],
                format="json",
            )

        assert r.status_code == 200
        profile = ExternalProfile.objects.get(user=user, kind="codeforces")
        assert navbat == [("profiles.refresh_external", profile.pk)], "LinkedIn'da reyting yo'q"

    def test_reyting_yangilanadi(self, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
        profile = ExternalProfile.objects.create(user=user, kind="codeforces", handle="tourist")
        monkeypatch.setitem(
            external.FETCHERS,
            "codeforces",
            lambda handle: {"rating": 3800, "max_rating": 4000, "rank": "legendary grandmaster"},
        )

        assert external.refresh(profile)
        profile.refresh_from_db()
        assert profile.rating == 3800
        assert profile.fetched_at is not None

    def test_tashqi_xato_jim_otadi(self, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
        profile = ExternalProfile.objects.create(user=user, kind="codeforces", handle="tourist")

        def yiqil(handle: str) -> dict[str, Any]:
            raise urllib.error.URLError("tarmoq yo'q")

        monkeypatch.setitem(external.FETCHERS, "codeforces", yiqil)

        assert external.refresh(profile) is False


@pytest.mark.django_db
class TestOmmaviyProfil:
    def test_standart_holatda_ochiq_pochta_esa_yopiq(self, user: User) -> None:
        """Ma'lumot standart holatda ochiq, pochta esa yopiq: mavjud hisoblar
        uni «ommaviy profilda ko'rinmaydi» sharti bilan bergan."""
        user.email = "aziz@example.com"
        user.school = "1-maktab"
        user.save(update_fields=["email", "school"])

        body = APIClient().get(reverse("user-profile", args=[user.username])).data

        assert body["info"] == {"school": "1-maktab"}

    def test_pochtani_egasi_ochsa_korinadi(self, user: User) -> None:
        user.email = "aziz@example.com"
        user.hidden_fields = []
        user.save(update_fields=["email", "hidden_fields"])

        body = APIClient().get(reverse("user-profile", args=[user.username])).data

        assert body["info"]["email"] == "aziz@example.com"

    def test_yashirilgan_maydon_faqat_egasiga_korinadi(self, user: User) -> None:
        user.email = "aziz@example.com"
        user.school = "1-maktab"
        user.hidden_fields = ["email"]
        user.save()

        begona = APIClient().get(reverse("user-profile", args=[user.username])).data
        egasi = kirgan(user).get(reverse("user-profile", args=[user.username])).data

        assert "email" not in begona["info"]
        assert begona["info"]["school"] == "1-maktab"
        assert egasi["info"]["email"] == "aziz@example.com"
        assert egasi["hidden_fields"] == ["email"]

    def test_ochirilgan_hisob_profili_yoq(self, user: User) -> None:
        account.anonymize(user)

        assert APIClient().get(reverse("user-profile", args=["aziz"])).status_code == 404

    def test_yutuqlar_hisoblanadi(self, user: User) -> None:
        user.streak_count = 8
        user.save(update_fields=["streak_count"])

        rows = {
            row["code"]: row
            for row in APIClient().get(reverse("user-achievements", args=[user.username])).data
        }

        assert rows["streak-7"]["done"] is True
        subset = {k: rows["streak-30"][k] for k in ("code", "group", "target", "progress", "done")}
        assert subset == {
            "code": "streak-30",
            "group": "streak",
            "target": 30,
            "progress": 8,
            "done": False,
        }
        assert rows["streak-30"]["tier"] == "silver"
        assert rows["solve-1"]["done"] is False

    def test_bosh_faoliyat(self, user: User) -> None:
        r = APIClient().get(reverse("user-activity", args=[user.username]))

        assert r.data == {"results": [], "next_before": None}


@pytest.mark.django_db
class TestObuna:
    def test_kuzatish_va_bekor_qilish(self, user: User, other_user: User) -> None:
        c = kirgan(user)
        url = reverse("user-follow", args=[other_user.username])

        assert c.post(url).data == {"followers": 1, "is_following": True}
        c.post(url)
        assert Follow.objects.count() == 1, "takror bosish ikkinchi yozuv ochmaydi"
        assert c.delete(url).data == {"followers": 0, "is_following": False}

    def test_ozini_kuzatib_bolmaydi(self, user: User) -> None:
        r = kirgan(user).post(reverse("user-follow", args=[user.username]))

        assert r.status_code == 400

    def test_royxatlar(self, user: User, other_user: User) -> None:
        Follow.objects.create(follower=user, following=other_user)

        obunachilar = APIClient().get(reverse("user-followers", args=[other_user.username]))
        kuzatilgan = APIClient().get(reverse("user-following", args=[user.username]))

        assert [u["username"] for u in obunachilar.data["results"]] == ["aziz"]
        assert [u["username"] for u in kuzatilgan.data["results"]] == ["bekzod"]


@pytest.mark.django_db
class TestJamoa:
    def yarat(self, user: User) -> dict[str, Any]:
        r = kirgan(user).post(reverse("me-teams"), {"name": "Kvarklar"}, format="json")
        assert r.status_code == 201
        return dict(r.data)

    def qoshil(self, user: User, code: str) -> Any:
        return kirgan(user).post(reverse("team-join"), {"code": code}, format="json")

    def test_yaratgan_odam_ega(self, user: User) -> None:
        team = self.yarat(user)

        assert team["role"] == "owner"
        assert [m["username"] for m in team["members"]] == ["aziz"]

    def test_havola_bilan_ham_qoshiladi(self, user: User, other_user: User) -> None:
        team = self.yarat(user)
        havola = f"https://rankwant.uz/settings/jamoalar?join={team['join_code']}"

        r = self.qoshil(other_user, havola)

        assert r.status_code == 200
        assert r.data["role"] == "member"
        assert len(r.data["members"]) == 2

    def test_yangilangan_kod_eskisini_yopadi(self, user: User, other_user: User) -> None:
        team = self.yarat(user)
        kirgan(user).post(reverse("team-refresh", args=[team["id"]]))

        assert self.qoshil(other_user, team["join_code"]).status_code == 400

    def test_ega_ketsa_egalik_otadi(self, user: User, other_user: User) -> None:
        team = self.yarat(user)
        self.qoshil(other_user, team["join_code"])

        assert kirgan(user).post(reverse("team-leave", args=[team["id"]])).status_code == 204
        member = TeamMember.objects.get(team_id=team["id"])
        assert (member.user, member.role) == (other_user, "owner")

    def test_yolgiz_ega_ketsa_jamoa_ochadi(self, user: User) -> None:
        team = self.yarat(user)

        kirgan(user).post(reverse("team-leave", args=[team["id"]]))

        assert not Team.objects.filter(pk=team["id"]).exists()

    def test_azo_boshqaruv_qila_olmaydi(self, user: User, other_user: User) -> None:
        team = self.yarat(user)
        self.qoshil(other_user, team["join_code"])
        azo = kirgan(other_user)

        assert azo.delete(reverse("team-detail", args=[team["id"]])).status_code == 403
        assert azo.delete(reverse("team-member", args=[team["id"], "aziz"])).status_code == 403

    def test_ega_azoni_chiqaradi(self, user: User, other_user: User) -> None:
        team = self.yarat(user)
        self.qoshil(other_user, team["join_code"])

        r = kirgan(user).delete(reverse("team-member", args=[team["id"], "bekzod"]))

        assert r.status_code == 204
        assert not TeamMember.objects.filter(team_id=team["id"], user=other_user).exists()

    def test_toliq_jamoaga_qoshilib_bolmaydi(self, user: User, other_user: User) -> None:
        team = teams.create(user, "Katta")
        for i in range(Team.MAX_MEMBERS - 1):
            teams.join(User.objects.create_user(username=f"azo{i}"), team.join_code)

        with pytest.raises(teams.TeamError):
            teams.join(other_user, team.join_code)


@pytest.mark.django_db
class TestKosmetika:
    def muqova(self, user: User, code: str) -> UserInventory:
        item = ShopItem.objects.create(
            code=code, category=ShopItem.Category.PROFILE_COVER, title_uz=code, price=100
        )
        return UserInventory.objects.create(user=user, item=item)

    def test_bitta_turkumda_bittasi_kiyiladi(self, user: User) -> None:
        a, b = self.muqova(user, "sinov-tun"), self.muqova(user, "sinov-dasht")
        c = kirgan(user)

        assert c.post(reverse("qvant-inventory-equip", args=[a.pk])).status_code == 200
        assert c.post(reverse("qvant-inventory-equip", args=[b.pk])).status_code == 200

        a.refresh_from_db()
        b.refresh_from_db()
        assert (a.is_equipped, b.is_equipped) == (False, True)
        profile = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert profile["cosmetics"]["cover"] == "sinov-dasht"

    def test_streak_freeze_kiyilmaydi(self, user: User) -> None:
        item = ShopItem.objects.create(
            code="sinov-freeze",
            category=ShopItem.Category.STREAK_FREEZE,
            title_uz="Freeze",
            price=200,
            is_consumable=True,
        )
        entry = UserInventory.objects.create(user=user, item=item)

        assert (
            kirgan(user).post(reverse("qvant-inventory-equip", args=[entry.pk])).status_code == 400
        )

    def test_begona_narsani_kiyib_bolmaydi(self, user: User, other_user: User) -> None:
        entry = self.muqova(other_user, "sinov-begona")

        r = kirgan(user).post(reverse("qvant-inventory-equip", args=[entry.pk]))

        assert r.status_code == 404

    def test_xaridlar_ommaviy(self, user: User) -> None:
        self.muqova(user, "sinov-tun")

        r = APIClient().get(reverse("user-purchases", args=[user.username]))

        assert [row["code"] for row in r.data] == ["sinov-tun"]


@pytest.mark.django_db
class TestHisobOchirilganda:
    def test_profil_qatorlari_va_boglanishlar_ochadi(
        self, user: User, other_user: User, skill: Skill
    ) -> None:
        UserSkill.objects.create(user=user, skill=skill, level=50)
        Follow.objects.create(follower=other_user, following=user)
        SocialAccount.objects.create(user=user, provider="google", uid="g1", email="a@b.uz")
        team = teams.create(user, "Jamoa")
        teams.join(other_user, team.join_code)

        account.anonymize(user)

        assert not UserSkill.objects.filter(user=user).exists()
        assert not Follow.objects.exists()
        assert not SocialAccount.objects.filter(user=user).exists()
        member = TeamMember.objects.get(team=team)
        assert (member.user, member.role) == (other_user, "owner"), "jamoa qoladi"

    def test_eksportda_profil_bolimlari_bor(self, user: User, skill: Skill) -> None:
        UserSkill.objects.create(user=user, skill=skill, level=70)

        data = account.export(user)

        assert data["skills"] == [{"skill__slug": "greedy", "level": 70}]
        assert {"technologies", "educations", "work", "teams", "sessions"} <= set(data)


@pytest.mark.django_db
class TestBildirishnomaKanallari:
    @pytest.fixture
    def telegramli(self, user: User) -> User:
        SocialAccount.objects.create(user=user, provider="telegram", uid="100", email="")
        return user

    def test_standart_faqat_sayt(self, telegramli: User, navbat: list[tuple[Any, ...]]) -> None:
        notify_services.notify(telegramli, Notification.Kind.DUEL, "Duel chaqiruvi")

        assert Notification.objects.filter(user=telegramli).count() == 1
        assert navbat == [], "Telegram'ga so'ramasdan yozilmaydi"

    def test_tanlangan_kanal_boyicha(self, telegramli: User, navbat: list[tuple[Any, ...]]) -> None:
        telegramli.notify_prefs = {"duel": {"site": False, "telegram": True}}
        telegramli.save(update_fields=["notify_prefs"])

        row = notify_services.notify(telegramli, Notification.Kind.DUEL, "Duel chaqiruvi")

        assert row is None
        assert not Notification.objects.filter(user=telegramli).exists()
        assert [call[:2] for call in navbat] == [("notifications.send_telegram", telegramli.pk)]

    def test_telegram_ulanmagan_bolsa_jim(self, user: User, navbat: list[tuple[Any, ...]]) -> None:
        user.notify_prefs = {"duel": {"telegram": True}}
        user.save(update_fields=["notify_prefs"])

        notify_services.notify(user, Notification.Kind.DUEL, "Duel")

        assert navbat == []

    def test_ommaviy_xabar_tanlovni_hurmat_qiladi(self, user: User, other_user: User) -> None:
        other_user.notify_prefs = {"system": {"site": False}}
        other_user.save(update_fields=["notify_prefs"])

        sent = notify_services.notify_many([user, other_user], Notification.Kind.SYSTEM, "Yangilik")

        assert sent == 1

    def test_bot_xabari(
        self, telegramli: User, settings: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings.TELEGRAM_BOT_TOKEN = "123:abc"
        yuborilgan: list[dict[str, Any]] = []

        def post(url: str, payload: dict[str, Any]) -> int:
            yuborilgan.append(payload)
            return 200

        monkeypatch.setattr("notifications.tasks._post", post)

        assert send_telegram(telegramli.pk, "Salom") == "sent"
        assert yuborilgan == [{"chat_id": 100, "text": "Salom", "disable_web_page_preview": True}]
