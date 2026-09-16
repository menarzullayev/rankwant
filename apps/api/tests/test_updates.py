"""Updates moduli — changelog.

Qaror sessiyasi: `docs/research/2026-09-13-rankwant-updates-design/DECISION-SESSION.md`.
Bu testlar **qarorlarni** tekshiradi, implementatsiya tafsilotini emas:
qaysi yozuv ko'rinadi, tarjima qanday tanlanadi, o'qilmagan holat kimga
tegishli.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from updates.models import SystemUpdate, SystemUpdateTranslation


@pytest.fixture
def staff_user(db) -> User:
    """Boshqaruv API'si faqat `is_staff` (core/staff.py)."""
    return User.objects.create_user("staff-updates", password="x", is_staff=True)


def make(**kw) -> SystemUpdate:
    """Nashr etilgan yozuv — standart holat."""
    data = {
        "title": "Masalalar filtri",
        "body": "Iyеrarxik filtr qo'shildi",
        "kind": SystemUpdate.Kind.NEW,
        "module": SystemUpdate.Module.PROBLEMS,
        "status": SystemUpdate.Status.PUBLISHED,
        "released_at": "2026-06-11",
    }
    data.update(kw)
    return SystemUpdate.objects.create(**data)


@pytest.mark.django_db
class TestKorinish:
    def test_nashr_etilgan_korinadi(self) -> None:
        make()
        body = APIClient().get(reverse("update-list")).json()
        assert body["count"] == 1

    def test_qoralama_korinmaydi(self) -> None:
        """Qaror 15-savol: tasdiqlanmagan yozuv ochiq lentaga chiqmaydi."""
        make(status=SystemUpdate.Status.DRAFT)
        assert APIClient().get(reverse("update-list")).json()["count"] == 0

    def test_nashrdan_olingan_lentada_korinmaydi(self) -> None:
        """Qaror 20-savol: nashrdan olinadi, lekin o'chirilmaydi."""
        row = make()
        row.status = SystemUpdate.Status.WITHDRAWN
        row.save()
        assert APIClient().get(reverse("update-list")).json()["count"] == 0

    def test_nashrdan_olingan_havolasi_ishlaydi(self) -> None:
        """Qaror 20-savol: `havola sindirilmaydi`.

        Ilgari bu yerda 404 kutilardi va izoh "batafsil hali ham
        ochiladi" deb yozib turardi — hujjat bilan test zid edi. Endi
        Telegram/Codeforces'dan kelgan havola ishlaydi, sahifa esa
        nashrdan olinganini aytadi.
        """
        row = make()
        row.status = SystemUpdate.Status.WITHDRAWN
        row.save()
        c = APIClient()
        res = c.get(reverse("update-detail", args=[row.pk]))
        assert res.status_code == 200
        assert res.json()["status"] == "withdrawn"

    def test_qoralama_havolasi_ham_yopiq(self) -> None:
        """Qaror 15-savol: tasdiqlanmagan yozuv ochiq o'qilmaydi."""
        row = make(status=SystemUpdate.Status.DRAFT)
        assert APIClient().get(reverse("update-detail", args=[row.pk])).status_code == 404

    def test_feature_flag_ochirilsa_korinmaydi(self) -> None:
        """Qaror 17-savol: rollback bir tugma — bazadan o'chirmasdan."""
        row = make(is_enabled=False)
        c = APIClient()
        assert c.get(reverse("update-list")).json()["count"] == 0
        # Modul darajasidagi rollback BATAFSILNI ham yopadi — u "butun
        # modul o'chirildi" degani, "bitta yozuv qaytarib olindi" emas.
        assert c.get(reverse("update-detail", args=[row.pk])).status_code == 404
        assert SystemUpdate.objects.filter(pk=row.pk).exists()

    def test_mehmon_ham_koradi(self) -> None:
        """Qaror 8-savol: mehmonga to'liq ko'rinadi (SEO + tashqi havola)."""
        make()
        assert APIClient().get(reverse("update-list")).status_code == 200


@pytest.mark.django_db
class TestTarjima:
    def test_tarjima_tanlanadi(self) -> None:
        row = make()
        SystemUpdateTranslation.objects.create(
            update=row, locale="en", title="Problem filter", body="Hierarchical filter"
        )
        item = APIClient().get(reverse("update-list"), {"lang": "en"}).json()["results"][0]
        assert item["title"] == "Problem filter"
        assert item["is_translated"] is True

    def test_tarjima_yoq_bolsa_kanonik(self) -> None:
        """Bo'sh sarlavha emas — o'zbekcha matn qaytadi (serializers.py izohi)."""
        make()
        item = APIClient().get(reverse("update-list"), {"lang": "zh"}).json()["results"][0]
        assert item["title"] == "Masalalar filtri"
        assert item["is_translated"] is False

    def test_tarjima_royxatda_ham_ishlaydi(self) -> None:
        row = make()
        SystemUpdateTranslation.objects.create(update=row, locale="ru", title="Фильтр")
        detail = APIClient().get(reverse("update-detail", args=[row.pk]), {"lang": "ru"}).json()
        assert detail["title"] == "Фильтр"


@pytest.mark.django_db
class TestOqilganHolat:
    def test_mehmon_uchun_none(self, user) -> None:
        """Qaror 8-savol: mehmonda o'qilmagan holat yo'q."""
        make()
        item = APIClient().get(reverse("update-list")).json()["results"][0]
        assert item["is_read"] is None

    def test_oqilmagan_soni(self, user) -> None:
        make()
        make(title="Ikkinchi", kind=SystemUpdate.Kind.FIXED)
        c = APIClient()
        c.force_authenticate(user)
        assert c.get(reverse("update-unread-count")).json()["count"] == 2

    def test_oqilgan_deb_belgilash(self, user) -> None:
        row = make()
        c = APIClient()
        c.force_authenticate(user)
        assert c.post(reverse("update-mark-read"), {"ids": [row.pk]}, format="json").json() == {
            "updated": 1
        }
        assert c.get(reverse("update-unread-count")).json()["count"] == 0

    def test_hammasi_oqildi(self, user) -> None:
        """`ids` yuborilmasa — hammasi (qaror: 'Hammasi o'qildi' tugmasi)."""
        make()
        make(title="Ikkinchi")
        c = APIClient()
        c.force_authenticate(user)
        assert c.post(reverse("update-mark-read"), {}, format="json").json()["updated"] == 2

    def test_takroriy_belgilash_xato_bermaydi(self, user) -> None:
        """Ikki qurilmada bosilsa yoki ikki marta bosilsa."""
        row = make()
        c = APIClient()
        c.force_authenticate(user)
        c.post(reverse("update-mark-read"), {"ids": [row.pk]}, format="json")
        assert c.post(reverse("update-mark-read"), {"ids": [row.pk]}, format="json").json() == {
            "updated": 0
        }

    def test_modul_boyicha_oqilmagan(self, user) -> None:
        """Nav chipi uchun (qaror 6-savol)."""
        make()
        make(title="Contest yangiligi", module=SystemUpdate.Module.CONTESTS)
        c = APIClient()
        c.force_authenticate(user)
        rows = c.get(reverse("update-unread-by-module")).json()
        assert {r["module"] for r in rows} == {"problems", "contests"}

    def test_oqilgan_modul_chiqmaydi(self, user) -> None:
        row = make()
        c = APIClient()
        c.force_authenticate(user)
        c.post(reverse("update-mark-read"), {"ids": [row.pk]}, format="json")
        assert c.get(reverse("update-unread-by-module")).json() == []

    def test_mehmon_oqilmagan_soray_olmaydi(self) -> None:
        make()
        assert APIClient().get(reverse("update-unread-count")).status_code in (401, 403)


@pytest.mark.django_db
class TestHarakatgaChaqiruv:
    @pytest.mark.parametrize("kind", ["breaking", "deprecated"])
    def test_chaqiruvchi_turlar(self, kind: str) -> None:
        item = make(kind=kind)
        assert item.is_actionable is True

    @pytest.mark.parametrize("kind", ["new", "fixed", "design", "content"])
    def test_oddiy_turlar(self, kind: str) -> None:
        item = make(kind=kind)
        assert item.is_actionable is False

    def test_chaqiruvchi_soni_alohida(self, user) -> None:
        """Buzuvchi yozuv alohida sanaladi — UI uni yashirmaydi."""
        make(kind=SystemUpdate.Kind.BREAKING)
        make(title="Oddiy", kind=SystemUpdate.Kind.FIXED)
        c = APIClient()
        c.force_authenticate(user)
        body = c.get(reverse("update-unread-count")).json()
        assert body == {"count": 2, "actionable": 1}


@pytest.mark.django_db
class TestArxiv:
    """Arxiv sahifasi tayanadigan so'rovlar (ochiq qavat)."""

    def test_tur_boyicha_filtr(self) -> None:
        make(kind=SystemUpdate.Kind.NEW)
        make(title="Tuzatish", kind=SystemUpdate.Kind.FIXED)
        body = APIClient().get(reverse("update-list"), {"kind": "fixed"}).json()
        assert body["count"] == 1
        assert body["results"][0]["kind"] == "fixed"

    def test_modul_boyicha_filtr(self) -> None:
        make(module=SystemUpdate.Module.PROBLEMS)
        make(title="Musobaqa", module=SystemUpdate.Module.CONTESTS)
        body = APIClient().get(reverse("update-list"), {"module": "contests"}).json()
        assert body["count"] == 1

    def test_qidiruv_ishlaydi(self) -> None:
        """`search_fields` ilgari JONLI EMAS edi.

        `filter_backends` e'lon qilinmagani uchun `DEFAULT_FILTER_BACKENDS`
        ishlardi va unda `SearchFilter` yo'q — ya'ni `?search=` hech narsa
        qilmasdan to'liq ro'yxatni qaytarardi.
        """
        make(title="Masalalar filtri")
        make(title="Musobaqa jadvali")
        body = APIClient().get(reverse("update-list"), {"search": "jadval"}).json()
        assert body["count"] == 1
        assert body["results"][0]["title"] == "Musobaqa jadvali"

    def test_sahifalash(self) -> None:
        for index in range(3):
            make(title=f"Yozuv {index}")
        body = APIClient().get(reverse("update-list"), {"page_size": 2}).json()
        assert body["count"] == 3
        assert len(body["results"]) == 2

    def test_chaqiruvchi_blok_alohida_sorov(self) -> None:
        """`/updates/actionable/` — arxiv tepasidagi blok.

        Bu yozuvlar kam uchraydi, ya'ni sahifalangan ro'yxatda umuman
        bo'lmasligi mumkin — shuning uchun alohida so'rov kerak.
        """
        make(kind=SystemUpdate.Kind.BREAKING, title="API o'zgardi")
        make(kind=SystemUpdate.Kind.DEPRECATED, title="Eski usul yopiladi")
        make(title="Oddiy yangilik", kind=SystemUpdate.Kind.NEW)
        rows = APIClient().get(reverse("update-actionable")).json()
        assert {r["title"] for r in rows} == {"API o'zgardi", "Eski usul yopiladi"}

    def test_chaqiruvchi_blok_nashrdan_olinganni_chiqarmaydi(self) -> None:
        row = make(kind=SystemUpdate.Kind.BREAKING)
        row.status = SystemUpdate.Status.WITHDRAWN
        row.save()
        assert APIClient().get(reverse("update-actionable")).json() == []

    def test_mehmon_chaqiruvchi_blokni_koradi(self) -> None:
        """Qaror 8-savol: mehmonga to'liq ko'rinadi."""
        make(kind=SystemUpdate.Kind.BREAKING)
        assert APIClient().get(reverse("update-actionable")).status_code == 200


@pytest.mark.django_db
class TestStaff:
    def test_staff_royxatdan_otmagan_kirolmaydi(self, user) -> None:
        c = APIClient()
        c.force_authenticate(user)
        assert c.get(reverse("staff-update-list")).status_code == 403

    def test_staff_nashr_qiladi(self, staff_user) -> None:
        row = make(status=SystemUpdate.Status.DRAFT)
        c = APIClient()
        c.force_authenticate(staff_user)
        assert c.post(reverse("staff-update-publish", args=[row.pk])).status_code == 200
        row.refresh_from_db()
        assert row.status == SystemUpdate.Status.PUBLISHED
        assert row.published_at is not None

    def test_staff_tarjima_bilan_yaratadi(self, staff_user) -> None:
        c = APIClient()
        c.force_authenticate(staff_user)
        payload = {
            "title": "Yangi filtr",
            "body": "matn",
            "kind": "new",
            "module": "problems",
            "status": "published",
            "released_at": "2026-09-13",
            "translations": [{"locale": "en", "title": "New filter", "body": "text"}],
        }
        assert c.post(reverse("staff-update-list"), payload, format="json").status_code == 201
        row = SystemUpdate.objects.get(title="Yangi filtr")
        assert row.translations.get(locale="en").title == "New filter"

    def test_staff_nashrdan_oladi(self, staff_user) -> None:
        row = make()
        c = APIClient()
        c.force_authenticate(staff_user)
        assert c.post(reverse("staff-update-withdraw", args=[row.pk])).status_code == 200
        row.refresh_from_db()
        assert row.status == SystemUpdate.Status.WITHDRAWN
