"""Staff maktab katalogi — `staff/schools/` (ADR-0017).

Nega alohida test: bu API katalogni to'ldirishning YAGONA yo'li.
`ADMIN_ENABLED` production'da ataylab o'chiq, `SchoolViewSet` esa faqat
o'qish uchun — ya'ni bu yuza ishlamasa, maktab reytingi va sinfdoshlar
bo'sh qolib ketadi.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import ApiToken, School, User


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff_school", password="x", is_staff=True)


@pytest.fixture
def staff_client(staff) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=staff)  # sessiya: request.auth = None
    return c


@pytest.mark.django_db
class TestStaffSchoolAccess:
    def test_anonim_kira_olmaydi(self) -> None:
        assert APIClient().get(reverse("staff-school-list")).status_code in (401, 403)

    def test_oddiy_foydalanuvchi_kira_olmaydi(self, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("staff-school-list")).status_code == 403

    def test_pat_bilan_o_zgartirib_bolmaydi(self, staff) -> None:
        """Xodimning `read` tokeni sizsa ham katalog o'zgarmasligi kerak."""
        _, raw = ApiToken.issue(staff, "t", ["read"], timezone.now() + timedelta(days=1))
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert c.get(reverse("staff-school-list")).status_code == 403
        assert (
            c.post(
                reverse("staff-school-list"), {"name": "Token maktabi"}, format="json"
            ).status_code
            == 403
        )
        assert not School.objects.filter(name="Token maktabi").exists()

    def test_staff_sessiya_bilan_kiradi(self, staff_client) -> None:
        assert staff_client.get(reverse("staff-school-list")).status_code == 200


@pytest.mark.django_db
class TestStaffSchoolCrud:
    def test_yaratish(self, staff_client) -> None:
        r = staff_client.post(
            reverse("staff-school-list"),
            {
                "name": "1-son umumta'lim maktabi",
                "kind": "school",
                "region": "samarqand",
                "district": "urgut",
            },
            format="json",
        )
        assert r.status_code == 201
        school = School.objects.get(name="1-son umumta'lim maktabi")
        assert school.region == "samarqand"
        # Katalog yozuvi darhol faol bo'ladi: moderator uni keyin
        # o'chirib qo'yishi mumkin, lekin standart holat — ko'rinadigan.
        assert school.is_active is True

    def test_tahrirlash(self, staff_client) -> None:
        school = School.objects.create(name="Eski nom")
        r = staff_client.patch(
            reverse("staff-school-detail", args=[school.pk]),
            {"name": "Yangi nom", "kind": "lyceum"},
            format="json",
        )
        assert r.status_code == 200
        school.refresh_from_db()
        assert school.name == "Yangi nom"
        assert school.kind == "lyceum"

    def test_ochirish(self, staff_client) -> None:
        school = School.objects.create(name="Vaqtinchalik")
        r = staff_client.delete(reverse("staff-school-detail", args=[school.pk]))
        assert r.status_code == 204
        assert not School.objects.filter(pk=school.pk).exists()

    def test_members_soni_keladi(self, staff_client, user) -> None:
        """Moderator o'chirishdan OLDIN nechta odam bog'langanini ko'radi:
        FK `SET_NULL`, ya'ni o'chirilsa ular `school_ref` ni yo'qotadi."""
        school = School.objects.create(name="Katta maktab")
        user.school_ref = school
        user.save()
        r = staff_client.get(reverse("staff-school-detail", args=[school.pk]))
        assert r.json()["members"] == 1

    def test_qidiruv(self, staff_client) -> None:
        School.objects.create(name="Al-Xorazmiy maktabi")
        School.objects.create(name="Butunlay boshqa maktab")
        r = staff_client.get(reverse("staff-school-list"), {"search": "Xorazmiy"})
        assert r.json()["count"] == 1

    def test_nom_majburiy(self, staff_client) -> None:
        r = staff_client.post(reverse("staff-school-list"), {"region": "buxoro"}, format="json")
        assert r.status_code == 400
        # Xato loyihaning yagona konvertida keladi (`08-technical-spec`):
        # tafsilot `error.details` ichida, yuqori darajada emas.
        assert "name" in r.json()["error"]["details"]
