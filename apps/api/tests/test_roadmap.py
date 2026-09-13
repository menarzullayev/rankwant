"""Roadmap moduli — taxta, ovoz, taklif, izoh.

Bu testlar **qarorlarni** tekshiradi, implementatsiya tafsilotini emas:
kim ovoz bera oladi, taklif qanday holatda tug'iladi, yashirilgan izoh
ko'rinadimi, va hisob-kitob to'g'rimi.
"""

from __future__ import annotations

import pytest
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from roadmap.models import RoadmapComment, RoadmapItem, RoadmapVote


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user("staff-roadmap", password="x", is_staff=True)


@pytest.fixture
def other(db) -> User:
    return User.objects.create_user("dilnoza", password="x")


def make(**kw) -> RoadmapItem:
    """Standart band — jamoa yozgan, rejalashtirilgan."""
    data = {
        "title": "Qorong'i rejim",
        "body": "Kechqurun ko'zni charchatmaydi",
        "status": RoadmapItem.Status.PLANNED,
    }
    data.update(kw)
    return RoadmapItem.objects.create(**data)


@pytest.mark.django_db
class TestTaqta:
    def test_band_mehmonga_korinadi(self) -> None:
        make()
        body = APIClient().get(reverse("platform-roadmap-list")).json()
        assert body["count"] == 1
        assert body["results"][0]["status"] == "planned"

    def test_feature_flag_ochirilsa_korinmaydi(self) -> None:
        make(is_enabled=False)
        assert APIClient().get(reverse("platform-roadmap-list")).json()["count"] == 0

    def test_rad_etilgan_royxatda_bor_ustunda_yoq(self) -> None:
        """Rad etilgan taklif yashirilmaydi — lekin kanban ustuni emas.

        Yashirilsa "taklif berdim, javob bo'lmadi" taassuroti qoladi;
        ustun bo'lsa "nima rejalashtirilgan" savoli xiralashadi.
        """
        make(status=RoadmapItem.Status.DECLINED)
        body = APIClient().get(reverse("platform-roadmap-list")).json()
        assert body["count"] == 1
        assert "declined" not in RoadmapItem.COLUMNS

    def test_tur_boyicha_filtr(self) -> None:
        make(status=RoadmapItem.Status.PLANNED)
        make(title="Boshqa", status=RoadmapItem.Status.RELEASED)
        body = APIClient().get(
            reverse("platform-roadmap-list"), {"status": "released"}
        ).json()
        assert body["count"] == 1
        assert body["results"][0]["status"] == "released"

    def test_qidiruv_ishlaydi(self) -> None:
        make(title="Qorong'i rejim")
        make(title="Turnir jadvali")
        body = APIClient().get(
            reverse("platform-roadmap-list"), {"search": "turnir"}
        ).json()
        assert body["count"] == 1

    def test_standart_tartib_barqaror(self) -> None:
        """`annotate()` dan keyin `Meta.ordering` kuchga KIRMAYDI.

        Usiz queryset tartibsiz qoladi va sahifalash beqaror bo'ladi:
        bir yozuv ikki marta chiqishi yoki umuman tushib qolishi mumkin
        (`UnorderedObjectListWarning`). Shuning uchun standart tartib
        viewset'da ochiq yozilgan.
        """
        birinchi = make(title="Birinchi")
        ikkinchi = make(title="Ikkinchi")
        rows = APIClient().get(reverse("platform-roadmap-list")).json()["results"]
        assert [r["id"] for r in rows] == [ikkinchi.pk, birinchi.pk]


@pytest.mark.django_db
class TestHisob:
    """Ovoz va izoh soni — `distinct=True` ning sababi shu testda."""

    def test_ikki_bogliqlanish_bir_birini_kopaytirmaydi(self, user, other) -> None:
        """3 ovoz + 2 izoh → `votes=3`, `comment_count=2`.

        `Count("vote_count")` va `Count("comments")` bir vaqtda `distinct`siz
        qo'shilsa cartesian hosil bo'ladi va ikkalasi ham `6` chiqadi.
        """
        item = make()
        third = User.objects.create_user("uchinchi", password="x")
        for voter in (user, other, third):
            RoadmapVote.objects.create(item=item, user=voter)
        RoadmapComment.objects.create(item=item, author=user, body="bir")
        RoadmapComment.objects.create(item=item, author=other, body="ikki")

        row = APIClient().get(reverse("platform-roadmap-list")).json()["results"][0]
        assert row["vote_count"] == 3
        assert row["comment_count"] == 2

    def test_yashirilgan_izoh_sanalmaydi(self, user) -> None:
        item = make()
        RoadmapComment.objects.create(item=item, author=user, body="ko'rinadi")
        RoadmapComment.objects.create(item=item, author=user, body="yashirin", is_hidden=True)
        row = APIClient().get(reverse("platform-roadmap-list")).json()["results"][0]
        assert row["comment_count"] == 1

    def test_ovoz_boyicha_tartiblash(self, user, other) -> None:
        """Rejalashtirilgan ustuni ovoz bo'yicha saralanadi."""
        kam = make(title="Kam ovoz")
        kop = make(title="Ko'p ovoz")
        third = User.objects.create_user("uchinchi", password="x")
        for voter in (user, other, third):
            RoadmapVote.objects.create(item=kop, user=voter)
        RoadmapVote.objects.create(item=kam, user=user)

        rows = APIClient().get(
            reverse("platform-roadmap-list"), {"ordering": "-vote_count"}
        ).json()["results"]
        assert [r["title"] for r in rows] == ["Ko'p ovoz", "Kam ovoz"]


@pytest.mark.django_db
class TestOvoz:
    def test_kirgan_ovoz_beradi(self, user) -> None:
        item = make()
        client = APIClient()
        client.force_authenticate(user)
        body = client.post(reverse("platform-roadmap-vote", args=[item.pk])).json()
        assert body == {"voted": True, "vote_count": 1}

    def test_ovozni_qaytarib_oladi(self, user) -> None:
        item = make()
        client = APIClient()
        client.force_authenticate(user)
        client.post(reverse("platform-roadmap-vote", args=[item.pk]))
        body = client.delete(reverse("platform-roadmap-vote", args=[item.pk])).json()
        assert body == {"voted": False, "vote_count": 0}

    def test_ikki_marta_bosilsa_son_ozgarmaydi(self, user) -> None:
        """Idempotentlik: ikki qurilmadan bir vaqtda bosilsa ham."""
        item = make()
        client = APIClient()
        client.force_authenticate(user)
        client.post(reverse("platform-roadmap-vote", args=[item.pk]))
        body = client.post(reverse("platform-roadmap-vote", args=[item.pk])).json()
        assert body == {"voted": True, "vote_count": 1}
        assert RoadmapVote.objects.filter(item=item).count() == 1

    def test_bir_odam_bir_ovoz(self, user) -> None:
        """Bazadagi `unique(item, user)` — ilova kodiga tayanmaydi."""
        item = make()
        RoadmapVote.objects.create(item=item, user=user)
        with pytest.raises(IntegrityError):
            RoadmapVote.objects.create(item=item, user=user)

    def test_mehmon_ovoz_berolmaydi(self) -> None:
        item = make()
        res = APIClient().post(reverse("platform-roadmap-vote", args=[item.pk]))
        assert res.status_code in (401, 403)

    def test_has_voted_faqat_ozimga(self, user, other) -> None:
        item = make()
        RoadmapVote.objects.create(item=item, user=other)

        anonymous = APIClient().get(reverse("platform-roadmap-list")).json()
        assert anonymous["results"][0]["has_voted"] is False

        client = APIClient()
        client.force_authenticate(user)
        mine = client.get(reverse("platform-roadmap-list")).json()
        assert mine["results"][0]["has_voted"] is False
        assert mine["results"][0]["vote_count"] == 1


@pytest.mark.django_db
class TestTaklif:
    def test_taklif_suggested_bolib_tugiladi(self, user) -> None:
        client = APIClient()
        client.force_authenticate(user)
        res = client.post(
            reverse("platform-roadmap-list"),
            {"title": "Turnir jadvali", "body": "Haftalik"},
            format="json",
        )
        assert res.status_code == 201
        assert res.json()["status"] == "suggested"
        assert res.json()["author"] == "aziz"

    def test_holatni_oz_bolicha_belgilab_bolmaydi(self, user) -> None:
        """Aks holda foydalanuvchi o'zini "chiqarildi" deb yozib qo'yardi."""
        client = APIClient()
        client.force_authenticate(user)
        res = client.post(
            reverse("platform-roadmap-list"),
            {"title": "Aldash", "body": "", "status": "released"},
            format="json",
        )
        assert res.status_code == 201
        assert res.json()["status"] == "suggested"

    def test_mehmon_taklif_berolmaydi(self) -> None:
        res = APIClient().post(
            reverse("platform-roadmap-list"), {"title": "X", "body": ""}, format="json"
        )
        assert res.status_code in (401, 403)

    def test_meniki_rad_etilganni_ham_koradi(self, user, other) -> None:
        mine = make(title="Meniki", author=user, status=RoadmapItem.Status.DECLINED)
        make(title="Boshqaniki", author=other)

        client = APIClient()
        client.force_authenticate(user)
        rows = client.get(reverse("platform-roadmap-mine")).json()
        assert [r["id"] for r in rows] == [mine.pk]

    def test_mehmon_meniki_soray_olmaydi(self) -> None:
        assert APIClient().get(reverse("platform-roadmap-mine")).status_code in (401, 403)


@pytest.mark.django_db
class TestIzoh:
    def test_mehmon_izohlarni_oqiydi(self, user) -> None:
        item = make()
        RoadmapComment.objects.create(item=item, author=user, body="Yaxshi fikr")
        rows = APIClient().get(reverse("platform-roadmap-comments", args=[item.pk])).json()
        assert rows[0]["body"] == "Yaxshi fikr"
        assert rows[0]["is_mine"] is False

    def test_kirgan_izoh_yozadi(self, user) -> None:
        item = make()
        client = APIClient()
        client.force_authenticate(user)
        res = client.post(
            reverse("platform-roadmap-comments", args=[item.pk]),
            {"body": "Menga ham kerak"},
            format="json",
        )
        assert res.status_code == 201
        assert res.json()["is_mine"] is True

    def test_mehmon_izoh_yozolmaydi(self) -> None:
        item = make()
        res = APIClient().post(
            reverse("platform-roadmap-comments", args=[item.pk]),
            {"body": "spam"},
            format="json",
        )
        assert res.status_code in (401, 403)

    def test_bosh_izoh_qabul_qilinmaydi(self, user) -> None:
        item = make()
        client = APIClient()
        client.force_authenticate(user)
        res = client.post(
            reverse("platform-roadmap-comments", args=[item.pk]),
            {"body": "   "},
            format="json",
        )
        assert res.status_code == 400

    def test_yashirilgan_izoh_chiqmaydi(self, user) -> None:
        """Post-moderatsiya: yashiriladi, o'chirilmaydi."""
        item = make()
        comment = RoadmapComment.objects.create(item=item, author=user, body="yashir")
        comment.is_hidden = True
        comment.save(update_fields=["is_hidden"])
        rows = APIClient().get(reverse("platform-roadmap-comments", args=[item.pk])).json()
        assert rows == []
        assert RoadmapComment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
class TestStaff:
    def test_staff_bolmagan_kirolmaydi(self, user) -> None:
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(reverse("staff-platform-roadmap-list")).status_code == 403

    def test_holat_ozgarishi_vaqtni_yozadi(self, staff_user) -> None:
        item = make(status=RoadmapItem.Status.SUGGESTED)
        client = APIClient()
        client.force_authenticate(staff_user)
        res = client.post(
            reverse("staff-platform-roadmap-set-status", args=[item.pk]),
            {"status": "planned"},
            format="json",
        )
        assert res.status_code == 200
        item.refresh_from_db()
        assert item.status == "planned"
        assert item.planned_at is not None

    def test_vaqt_qayta_yozilmaydi(self, staff_user) -> None:
        """Band orqaga qaytarilib yana oldinga o'tkazilsa tarix o'zgarmasin."""
        item = make(status=RoadmapItem.Status.PLANNED)
        client = APIClient()
        client.force_authenticate(staff_user)
        client.post(
            reverse("staff-platform-roadmap-set-status", args=[item.pk]),
            {"status": "planned"},
            format="json",
        )
        item.refresh_from_db()
        first = item.planned_at
        client.post(
            reverse("staff-platform-roadmap-set-status", args=[item.pk]),
            {"status": "suggested"},
            format="json",
        )
        client.post(
            reverse("staff-platform-roadmap-set-status", args=[item.pk]),
            {"status": "planned"},
            format="json",
        )
        item.refresh_from_db()
        assert item.planned_at == first

    def test_notogri_holat_rad_etiladi(self, staff_user) -> None:
        item = make()
        client = APIClient()
        client.force_authenticate(staff_user)
        res = client.post(
            reverse("staff-platform-roadmap-set-status", args=[item.pk]),
            {"status": "yoq-bunday"},
            format="json",
        )
        assert res.status_code == 400

    def test_holat_filtri_ishlaydi(self, staff_user) -> None:
        """`StaffViewSet` da `filterset_fields` JONSIZ edi — shu tekshiruv
        `DjangoFilterBackend` ro'yxatda borligini kafolatlaydi."""
        make(status=RoadmapItem.Status.PLANNED)
        make(title="Taklif", status=RoadmapItem.Status.SUGGESTED)
        client = APIClient()
        client.force_authenticate(staff_user)
        body = client.get(
            reverse("staff-platform-roadmap-list"), {"status": "suggested"}
        ).json()
        assert body["count"] == 1

    def test_izohni_yashirish(self, staff_user, user) -> None:
        item = make()
        comment = RoadmapComment.objects.create(item=item, author=user, body="spam")
        client = APIClient()
        client.force_authenticate(staff_user)
        assert (
            client.post(
                reverse("staff-platform-roadmap-comment-hide", args=[comment.pk])
            ).status_code
            == 200
        )
        comment.refresh_from_db()
        assert comment.is_hidden is True

        client.post(reverse("staff-platform-roadmap-comment-unhide", args=[comment.pk]))
        comment.refresh_from_db()
        assert comment.is_hidden is False
