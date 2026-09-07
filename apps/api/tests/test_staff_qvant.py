"""Staff API — quest va do'kon katalogi (`staff/quests/`, `staff/shop-items/`)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from qvant import quests
from qvant.models import QvantQuest, ShopItem, UserInventory, UserQuestCompletion


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff1", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    client = APIClient()
    client.force_authenticate(staff)
    return client


@pytest.fixture
def quest(db) -> QvantQuest:
    return QvantQuest.objects.create(
        code="daily_solve", type=QvantQuest.Type.DAILY, title_uz="Yeching", reward=10
    )


@pytest.fixture
def item(db) -> ShopItem:
    return ShopItem.objects.create(
        code="streak-freeze",
        category=ShopItem.Category.STREAK_FREEZE,
        title_uz="Freeze",
        price=200,
        is_consumable=True,
    )


@pytest.mark.django_db
class TestRuxsat:
    @pytest.mark.parametrize("name", ["staff-quest-list", "staff-shop-item-list"])
    def test_anonim(self, name) -> None:
        assert APIClient().get(reverse(name)).status_code in (401, 403)

    @pytest.mark.parametrize("name", ["staff-quest-list", "staff-shop-item-list"])
    def test_oddiy_foydalanuvchi(self, user, name) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(reverse(name)).status_code == 403
        assert client.post(reverse(name), {}).status_code == 403

    def test_sync_oddiy_foydalanuvchiga_yopiq(self, user) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.post(reverse("staff-quest-sync")).status_code == 403


@pytest.mark.django_db
class TestQuest:
    def test_royxat(self, staff_client, quest, user) -> None:
        UserQuestCompletion.objects.create(user=user, quest=quest, period_key="d", awarded=10)
        body = staff_client.get(reverse("staff-quest-list")).json()
        assert body["count"] == 1
        row = body["results"][0]
        assert row["code"] == "daily_solve"
        assert row["completion_count"] == 1
        assert row["is_active"] is True

    def test_qidiruv(self, staff_client, quest) -> None:
        QvantQuest.objects.create(code="streak_7", type="achievement", title_uz="Streak", reward=50)
        body = staff_client.get(reverse("staff-quest-list"), {"search": "streak"}).json()
        assert [r["code"] for r in body["results"]] == ["streak_7"]

    def test_yaratish(self, staff_client) -> None:
        res = staff_client.post(
            reverse("staff-quest-list"),
            {"code": "weekly_marathon", "type": "weekly", "title_uz": "Marafon", "reward": 100},
        )
        assert res.status_code == 201, res.json()
        assert res.json()["completion_count"] == 0
        assert QvantQuest.objects.get(code="weekly_marathon").reward == 100

    def test_takror_kod_rad_etiladi(self, staff_client, quest) -> None:
        res = staff_client.post(
            reverse("staff-quest-list"),
            {"code": "daily_solve", "type": "daily", "title_uz": "x", "reward": 1},
        )
        assert res.status_code == 400
        assert "code" in res.json()["error"]["details"]

    def test_tahrirlash(self, staff_client, quest) -> None:
        res = staff_client.patch(
            reverse("staff-quest-detail", args=["daily_solve"]),
            {"reward": 25, "is_active": False},
        )
        assert res.status_code == 200
        quest.refresh_from_db()
        assert (quest.reward, quest.is_active) == (25, False)

    def test_ochirish(self, staff_client, quest) -> None:
        res = staff_client.delete(reverse("staff-quest-detail", args=["daily_solve"]))
        assert res.status_code == 204
        assert not QvantQuest.objects.filter(code="daily_solve").exists()

    def test_sync_katalogni_tiklaydi(self, staff_client, quest) -> None:
        quest.reward = 999
        quest.is_active = False
        quest.save()
        QvantQuest.objects.create(code="custom", type="daily", title_uz="Qo'lda", reward=5)

        res = staff_client.post(reverse("staff-quest-sync"))
        assert res.status_code == 200
        assert res.json() == {"synced": len(quests.CATALOGUE)}
        quest.refresh_from_db()
        assert (quest.reward, quest.is_active) == (quests.CATALOGUE["daily_solve"][1], True)
        # Qo'lda qo'shilgan quest o'z holicha qoladi
        assert QvantQuest.objects.get(code="custom").reward == 5

    def test_ommaviy_api_ozgarmaydi(self, user, quest) -> None:
        client = APIClient()
        client.force_authenticate(user)
        row = client.get(reverse("qvant-quests")).json()[0]
        assert "is_active" not in row
        assert "completion_count" not in row


@pytest.mark.django_db
class TestShopItem:
    def test_royxat(self, staff_client, item, user) -> None:
        UserInventory.objects.create(user=user, item=item)
        body = staff_client.get(reverse("staff-shop-item-list")).json()
        assert body["count"] == 1
        row = body["results"][0]
        assert row["code"] == "streak-freeze"
        assert row["owner_count"] == 1
        assert row["asset_ref"] == ""

    def test_yaratish(self, staff_client) -> None:
        res = staff_client.post(
            reverse("staff-shop-item-list"),
            {
                "code": "gold-frame",
                "category": "avatar_frame",
                "title_uz": "Oltin ramka",
                "price": 500,
                "asset_ref": "frames/gold.svg",
            },
        )
        assert res.status_code == 201, res.json()
        created = ShopItem.objects.get(code="gold-frame")
        assert created.is_consumable is False
        assert created.asset_ref == "frames/gold.svg"

    def test_notogri_kategoriya(self, staff_client) -> None:
        res = staff_client.post(
            reverse("staff-shop-item-list"),
            {"code": "x", "category": "unlock_content", "title_uz": "x", "price": 1},
        )
        assert res.status_code == 400
        assert "category" in res.json()["error"]["details"]

    def test_tahrirlash(self, staff_client, item) -> None:
        res = staff_client.patch(
            reverse("staff-shop-item-detail", args=["streak-freeze"]),
            {"price": 150, "is_active": False},
        )
        assert res.status_code == 200
        item.refresh_from_db()
        assert (item.price, item.is_active) == (150, False)

    def test_ochirish(self, staff_client, item) -> None:
        res = staff_client.delete(reverse("staff-shop-item-detail", args=["streak-freeze"]))
        assert res.status_code == 204
        assert not ShopItem.objects.filter(code="streak-freeze").exists()

    def test_sotib_olingan_item_ochirilmaydi(self, staff_client, item, user) -> None:
        UserInventory.objects.create(user=user, item=item)
        res = staff_client.delete(reverse("staff-shop-item-detail", args=["streak-freeze"]))
        assert res.status_code == 400
        assert "code" in res.json()["error"]["details"]
        assert ShopItem.objects.filter(code="streak-freeze").exists()

    def test_ommaviy_dokon_nofaolni_korsatmaydi(self, staff_client, item) -> None:
        staff_client.patch(
            reverse("staff-shop-item-detail", args=["streak-freeze"]), {"is_active": False}
        )
        rows = APIClient().get(reverse("qvant-shop-list")).json()
        assert rows == []
