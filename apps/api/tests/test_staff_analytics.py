"""Voronka dashboardi — `AnalyticsEvent` ni KO'RISH yo'li (qaror 7).

Asosiy tekshiruv: sessiya bo'yicha SANALADI. Bitta odam xatoni bir
necha marta ko'rishi mumkin, «qancha odam shu qadamda to'xtadi»
savoliga esa faqat sessiya javob beradi — xom hodisa soni noto'g'ri
manzara berardi.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import AnalyticsEvent, ApiToken, User


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("analitik", password="x", is_staff=True)


@pytest.fixture
def oddiy(db) -> User:
    return User.objects.create_user("oddiy", password="x")


def yoz(name: str, session: str, **props: object) -> AnalyticsEvent:
    return AnalyticsEvent.objects.create(name=name, session_key=session, props=props)


def sorov(staff: User, **params: str | int) -> Any:
    """Staff endpoint'iga so'rov.

    `Any` qaytaradi: javob shakli test ichida tekshiriladi, mypy uchun
    to'liq tip yozish esa har bir maydon uchun ortiqcha e'lon bo'lardi.
    """
    c = APIClient()
    c.force_authenticate(user=staff)
    return c.get(reverse("staff-analytics"), params)


@pytest.mark.django_db
class TestKirish:
    def test_staff_kora_oladi(self, staff: User) -> None:
        assert sorov(staff).status_code == 200

    def test_oddiy_foydalanuvchi_rad_etiladi(self, oddiy: User) -> None:
        c = APIClient()
        c.force_authenticate(user=oddiy)
        assert c.get(reverse("staff-analytics")).status_code == 403

    def test_kirilmagan_rad_etiladi(self) -> None:
        assert APIClient().get(reverse("staff-analytics")).status_code in (401, 403)

    def test_pat_bilan_ishlamaydi(self, staff: User) -> None:
        """ADR-0008: staff yuzasi token bilan ochilmaydi."""
        _, raw = ApiToken.issue(staff, "t", ["read"], timezone.now() + timedelta(days=1))
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert c.get(reverse("staff-analytics")).status_code == 403


@pytest.mark.django_db
class TestVoronka:
    def test_sessiya_boyicha_sanaladi(self, staff: User) -> None:
        """Bir sessiya bir marta sanaladi — xom hodisa soni emas."""
        for _ in range(5):
            yoz("auth.form_started", "s1")
        yoz("auth.register_done", "s1")

        data = sorov(staff).json()

        started = data["funnel"][0]
        done = data["funnel"][1]
        assert started["sessions"] == 1
        assert done["sessions"] == 1

    def test_ikki_sessiya_ajratiladi(self, staff: User) -> None:
        yoz("auth.form_started", "s1")
        yoz("auth.form_started", "s2")
        yoz("auth.register_done", "s1")

        data = sorov(staff).json()

        assert data["funnel"][0]["sessions"] == 2
        assert data["funnel"][1]["sessions"] == 1

    def test_ulush_birinchi_qadamga_nisbatan(self, staff: User) -> None:
        for i in range(4):
            yoz("auth.form_started", f"s{i}")
        yoz("auth.register_done", "s0")

        data = sorov(staff).json()

        assert data["funnel"][0]["share"] == 100.0
        assert data["funnel"][1]["share"] == 25.0

    def test_bosh_hodisada_nolga_bolinmaydi(self, staff: User) -> None:
        """Hodisa bo'lmasa `share` 0 bo'lishi kerak — ZeroDivisionError emas."""
        data = sorov(staff).json()

        assert data["funnel"][0]["sessions"] == 0
        assert data["funnel"][0]["share"] == 0.0
        assert data["total_events"] == 0

    def test_oynadan_tashqari_hodisa_hisobga_olinmaydi(self, staff: User) -> None:
        eski = yoz("auth.form_started", "eski")
        AnalyticsEvent.objects.filter(pk=eski.pk).update(
            created_at=timezone.now() - timedelta(days=90)
        )
        yoz("auth.form_started", "yangi")

        data = sorov(staff, days=30).json()

        assert data["funnel"][0]["sessions"] == 1


@pytest.mark.django_db
class TestQadam2:
    def test_otkazib_yuborish_ulushi(self, staff: User) -> None:
        yoz("auth.step2_saved", "s1")
        for i in range(3):
            yoz("auth.step2_skipped", f"k{i}")

        data = sorov(staff).json()["step2"]

        assert data["saved"] == 1
        assert data["skipped"] == 3
        assert data["skipped_share"] == 75.0

    def test_bosh_holatda_nol(self, staff: User) -> None:
        data = sorov(staff).json()["step2"]

        assert data["saved"] == 0
        assert data["skipped_share"] == 0.0


@pytest.mark.django_db
class TestXatolar:
    def test_sabab_boyicha_guruhlanadi(self, staff: User) -> None:
        yoz("auth.form_error", "s1", reason="username_taken")
        yoz("auth.form_error", "s2", reason="username_taken")
        yoz("auth.form_error", "s3", reason="terms")

        data = sorov(staff).json()["errors"]

        assert data[0] == {"reason": "username_taken", "sessions": 2}
        assert data[1] == {"reason": "terms", "sessions": 1}

    def test_sababsiz_hodisa_ham_korinadi(self, staff: User) -> None:
        """`props` bo'sh bo'lsa qator yo'qolib qolmasin — aks holda
        jami xato soni dashboard'dagi yig'indiga to'g'ri kelmasdi."""
        yoz("auth.form_error", "s1")

        data = sorov(staff).json()["errors"]

        assert data[0]["reason"] == "—"
        assert data[0]["sessions"] == 1


@pytest.mark.django_db
class TestTaqsimot:
    def test_til_boyicha(self, staff: User) -> None:
        AnalyticsEvent.objects.create(name="auth.form_started", session_key="s1", locale="ru")
        AnalyticsEvent.objects.create(name="auth.form_started", session_key="s2", locale="uz")

        data = sorov(staff).json()["locales"]

        assert {row["locale"] for row in data} == {"ru", "uz"}

    def test_mamlakat_foydalanuvchidan_olinadi(self, staff: User, oddiy: User) -> None:
        oddiy.country = "KZ"
        oddiy.save(update_fields=["country"])
        AnalyticsEvent.objects.create(name="auth.form_started", session_key="s1", user=oddiy)

        data = sorov(staff).json()["countries"]

        assert data[0]["country"] == "KZ"

    def test_mamlakatisiz_hodisa_tushmaydi(self, staff: User) -> None:
        """Kirilmagan sessiyada `user` NULL — bu ro'yxatga kirmaydi."""
        yoz("auth.form_started", "anonim")

        assert sorov(staff).json()["countries"] == []

    def test_kunlik_ketma_ketlik(self, staff: User) -> None:
        yoz("auth.form_started", "s1")
        yoz("auth.register_done", "s1")

        data = sorov(staff).json()["daily"]

        assert len(data) == 1
        assert data[0]["started"] == 1
        assert data[0]["done"] == 1


@pytest.mark.django_db
class TestABGuruh:
    """A/B natijasi — `props.exp` bo'yicha ajratiladi (8-qaror).

    Guruhni `lib/analytics.ts` har bir hodisaga qo'shadi; bu yerda faqat
    jamlash sinaladi. Taqqoslanadigan ko'rsatkich — ro'yxatdan o'tishni
    TUGATGAN sessiyalar, chunki ikki guruhda farq qiladigan yagona
    narsa — viloyat qachon so'ralishi.
    """

    def test_guruhlar_ajratiladi(self, staff: User) -> None:
        AnalyticsEvent.objects.create(
            name="auth.register_done", session_key="a1", props={"exp": "a"}
        )
        for s in ("b1", "b2"):
            AnalyticsEvent.objects.create(
                name="auth.register_done", session_key=s, props={"exp": "b"}
            )

        data = sorov(staff).json()["variant"]

        assert data["control"] == 1
        assert data["variant"] == 2
        assert data["total"] == 3
        assert data["control_share"] == 33.3

    def test_guruhsiz_hodisa_hisobga_olinmaydi(self, staff: User) -> None:
        """Cookie o'chirilgan bo'lsa `exp` yo'q. Uni «nazorat» deb
        yozish nazorat guruhini sun'iy shishirib, natijani buzardi."""
        yoz("auth.register_done", "s1")

        data = sorov(staff).json()["variant"]

        assert data["total"] == 0
        assert data["control_share"] == 0.0

    def test_faqat_tugatganlar_sanaladi(self, staff: User) -> None:
        """Boshlaganlar emas: «erta so'rash qaytarib yubordimi» degan
        savolga faqat yakuniy qadam javob beradi."""
        for s in ("a1", "a2"):
            AnalyticsEvent.objects.create(
                name="auth.form_started", session_key=s, props={"exp": "a"}
            )

        assert sorov(staff).json()["variant"]["total"] == 0

    def test_notanish_guruh_e_tiborsiz(self, staff: User) -> None:
        """Kutilmagan qiymat (eski mijoz, qo'lda o'zgartirilgan cookie)
        hech bir guruhga qo'shilmaydi."""
        AnalyticsEvent.objects.create(
            name="auth.register_done", session_key="x", props={"exp": "z"}
        )

        assert sorov(staff).json()["variant"]["total"] == 0


@pytest.mark.django_db
class TestOyna:
    """`days` parametri — chegaralar va noto'g'ri qiymatlar.

    Yuqori chegara muhim: usiz `days=99999` butun jadvalni skanerlab
    ketardi va bu endpoint'ni sekinlashtirish yo'li bo'lardi.
    """

    def test_standart_30_kun(self, staff: User) -> None:
        assert sorov(staff).json()["window_days"] == 30

    def test_qiymat_qabul_qilinadi(self, staff: User) -> None:
        assert sorov(staff, days=7).json()["window_days"] == 7

    @pytest.mark.parametrize("qiymat", ["0", "-5"])
    def test_past_chegara(self, staff: User, qiymat: str) -> None:
        assert sorov(staff, days=qiymat).json()["window_days"] == 1

    def test_yuqori_chegara(self, staff: User) -> None:
        """Cheklovsiz so'rov butun jadvalni skanerlab ketardi."""
        assert sorov(staff, days=99999).json()["window_days"] == 365

    @pytest.mark.parametrize("qiymat", ["abc", "1.5", ""])
    def test_notogri_qiymat_400(self, staff: User, qiymat: str) -> None:
        assert sorov(staff, days=qiymat).status_code == 400
