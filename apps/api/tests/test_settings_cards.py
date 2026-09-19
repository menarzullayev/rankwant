"""Settings cards: Ma'lumotlar, Karyera, Ko'nikmalar, Profil."""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from profiles.models import Education, UserSkillBadge, WorkExperience
from qvant import ledger
from qvant.models import QvantTransaction, ShopItem, UserInventory


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def yoz(user: User, body: dict[str, Any]) -> Any:
    return kirgan(user).patch(reverse("me"), body, format="json")


@pytest.mark.django_db
class TestMalumotlar:
    def test_gender_and_privacy(self, user: User) -> None:
        r = yoz(user, {"gender": "female", "hidden_fields": ["email", "gender"]})

        assert r.status_code == 200, r.data
        assert r.data["gender"] == "female"
        public = APIClient().get(reverse("user-profile", args=[user.username])).data
        own = kirgan(user).get(reverse("user-profile", args=[user.username])).data
        assert "gender" not in public["info"]
        assert own["info"]["gender"] == "female"

    def test_bad_gender_rejected(self, user: User) -> None:
        assert yoz(user, {"gender": "other"}).status_code == 400

    def test_websites_replace_and_sync_first(self, user: User) -> None:
        urls = ["https://one.dev/", "https://two.dev/"]
        r = yoz(user, {"websites": urls})

        assert r.status_code == 200, r.data
        assert r.data["websites"] == urls
        assert r.data["website"] == urls[0]
        user.refresh_from_db()
        assert user.website == urls[0]

    def test_websites_cap_and_invalid(self, user: User) -> None:
        too_many = [f"https://n{i}.dev/" for i in range(6)]
        assert yoz(user, {"websites": too_many}).status_code == 400
        assert yoz(user, {"websites": ["not-a-url"]}).status_code == 400

    def test_website_patch_merges_into_list(self, user: User) -> None:
        yoz(user, {"websites": ["https://old.dev/", "https://keep.dev/"]})
        r = yoz(user, {"website": "https://new.dev/"})

        assert r.status_code == 200
        assert r.data["websites"][0] == "https://new.dev/"
        assert r.data["websites"][1] == "https://keep.dev/"

    def test_delivery_all_or_nothing(self, user: User) -> None:
        partial = yoz(user, {"postal_recipient": "Ali Valiyev", "postal_consent": True})
        assert partial.status_code == 400

        full = {
            "postal_recipient": "Ali Valiyev",
            "postal_country": "uz",
            "postal_region": "Tashkent",
            "postal_city": "Tashkent",
            "postal_address": "Amir Temur 1",
            "postal_code": "100000",
            "postal_recipient_native": "Ali Valiyev",
            "postal_region_native": "Toshkent",
            "postal_city_native": "Toshkent",
            "postal_address_native": "Amir Temur ko'chasi 1",
            "postal_consent": True,
            "shirt_size_eu": "50",
        }
        r = yoz(user, full)
        assert r.status_code == 200, r.data
        assert r.data["postal_country"] == "UZ"
        assert r.data["shirt_size_eu"] == "50"
        public = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert "postal_address" not in public
        assert "postal_address" not in public.get("info", {})

    def test_delivery_erase(self, user: User) -> None:
        yoz(
            user,
            {
                "postal_recipient": "Ali Valiyev",
                "postal_country": "UZ",
                "postal_region": "Tashkent",
                "postal_city": "Tashkent",
                "postal_address": "Amir Temur 1",
                "postal_code": "100000",
                "postal_recipient_native": "Ali Valiyev",
                "postal_region_native": "Toshkent",
                "postal_city_native": "Toshkent",
                "postal_address_native": "Amir Temur 1",
                "postal_consent": True,
            },
        )
        r = yoz(
            user,
            {
                "postal_recipient": "",
                "postal_country": "",
                "postal_region": "",
                "postal_city": "",
                "postal_address": "",
                "postal_code": "",
                "postal_recipient_native": "",
                "postal_region_native": "",
                "postal_city_native": "",
                "postal_address_native": "",
                "postal_consent": False,
            },
        )
        assert r.status_code == 200, r.data
        user.refresh_from_db()
        assert user.postal_address == ""
        assert user.postal_consent is False

    def test_heatmap_hidden_from_strangers(self, user: User, other_user: User) -> None:
        yoz(user, {"hidden_fields": ["email", "heatmap", "activity", "recent_ac"]})
        guest = APIClient()
        cal = guest.get(reverse("user-calendar", args=[user.username]))
        act = guest.get(reverse("user-activity", args=[user.username]))
        mmap = guest.get(reverse("user-problem-map", args=[user.username]))
        assert cal.data["hidden"] is True
        assert cal.data["days"] == []
        assert act.data == {"results": [], "next_before": None, "hidden": True}
        assert mmap.data == {"problems": [], "hidden": True}

        own = kirgan(user).get(reverse("user-calendar", args=[user.username]))
        assert "hidden" not in own.data
        stranger = kirgan(other_user).get(reverse("user-activity", args=[user.username]))
        assert stranger.data["hidden"] is True


@pytest.mark.django_db
class TestKaryera:
    def test_month_and_present(self, user: User) -> None:
        body = [
            {
                "organization": "TATU",
                "degree": "Bakalavr",
                "start_year": 2020,
                "start_month": 9,
                "end_year": 2024,
                "end_month": 6,
                "current": False,
            }
        ]
        r = kirgan(user).put(reverse("me-educations"), body, format="json")
        assert r.status_code == 200, r.data
        assert r.data[0]["start_month"] == 9
        assert r.data[0]["end_month"] == 6

        work = [
            {
                "company": "EPAM",
                "title": "Backend",
                "start_year": 2024,
                "start_month": 2,
                "current": True,
                "end_year": 2025,
                "end_month": 1,
            }
        ]
        r = kirgan(user).put(reverse("me-work"), work, format="json")
        assert r.status_code == 200, r.data
        assert r.data[0]["current"] is True
        assert r.data[0]["end_year"] is None
        assert r.data[0]["end_month"] is None
        assert WorkExperience.objects.get(user=user).current is True

    def test_end_before_start_with_months(self, user: User) -> None:
        body = [
            {
                "organization": "TATU",
                "start_year": 2024,
                "start_month": 6,
                "end_year": 2024,
                "end_month": 1,
            }
        ]
        assert kirgan(user).put(reverse("me-educations"), body, format="json").status_code == 400

    def test_public_profile_includes_months(self, user: User) -> None:
        Education.objects.create(
            user=user, organization="TATU", start_year=2020, start_month=9, current=True
        )
        profile = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert profile["educations"][0]["start_month"] == 9
        assert profile["educations"][0]["current"] is True


@pytest.mark.django_db
class TestKonikmalar:
    def test_badge_crud_and_public(self, user: User) -> None:
        body = [{"text": "Python", "icon": "python", "color": "#3776AB"}]
        r = kirgan(user).put(reverse("me-skill-badges"), body, format="json")
        assert r.status_code == 200, r.data
        assert r.data[0]["color"] == "#3776ab"
        profile = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert profile["badges"] == [{"text": "Python", "icon": "python", "color": "#3776ab"}]

    def test_badge_validation(self, user: User) -> None:
        c = kirgan(user)
        assert (
            c.put(
                reverse("me-skill-badges"),
                [{"text": "X", "icon": "cobol", "color": "#000000"}],
                format="json",
            ).status_code
            == 400
        )
        assert (
            c.put(
                reverse("me-skill-badges"),
                [{"text": "X", "icon": "python", "color": "blue"}],
                format="json",
            ).status_code
            == 400
        )
        too_many = [{"text": f"B{i}", "icon": "python", "color": "#000000"} for i in range(11)]
        assert c.put(reverse("me-skill-badges"), too_many, format="json").status_code == 400
        assert not UserSkillBadge.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestProfil:
    def test_english_names_owner_only(self, user: User) -> None:
        r = yoz(user, {"first_name_en": "Ali", "last_name_en": "Valiyev"})
        assert r.status_code == 200, r.data
        me = kirgan(user).get(reverse("me")).data
        public = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert (me["first_name_en"], me["last_name_en"]) == ("Ali", "Valiyev")
        assert "first_name_en" not in public
        assert "first_name" not in public

    def test_buy_cover_from_shop(self, user: User) -> None:
        ShopItem.objects.create(
            code="cover-night",
            category=ShopItem.Category.PROFILE_COVER,
            title_uz="Tungi cover",
            price=800,
        )
        ledger.credit(user, 800, QvantTransaction.Reason.ADMIN)
        r = kirgan(user).post(reverse("qvant-shop-purchase"), {"item": "cover-night"})
        assert r.status_code == 201, r.data
        entry_id = r.data["id"]
        wear = kirgan(user).post(reverse("qvant-inventory-equip", args=[entry_id]))
        assert wear.status_code == 200
        profile = APIClient().get(reverse("user-profile", args=[user.username])).data
        assert profile["cosmetics"]["cover"] == "cover-night"
        assert UserInventory.objects.filter(user=user, item__code="cover-night").exists()
