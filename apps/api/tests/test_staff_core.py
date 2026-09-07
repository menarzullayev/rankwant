"""Staff yuzasi bazasi — PAT rad etiladi (ADR-0008), sessiya ishlaydi."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import ApiToken, User


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user("staff_core", password="x", is_staff=True)


@pytest.mark.django_db
class TestStaffSurfaceAuth:
    @pytest.mark.parametrize("scopes", [["read"], ["submit"], ["contest:manage"]])
    def test_pat_har_qanday_scope_bilan_rad_etiladi(self, staff, problem, scopes) -> None:
        """Xodimning tokeni sizsa ham boshqaruvga yo'l ochilmaydi."""
        _, raw = ApiToken.issue(staff, "t", scopes, timezone.now() + timedelta(days=1))
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert c.get(reverse("staff-problem-list")).status_code == 403
        r = c.patch(
            reverse("staff-problem-detail", args=[problem.slug]), {"title": "x"}, format="json"
        )
        assert r.status_code == 403
        problem.refresh_from_db()
        assert problem.title != "x"

    def test_sessiya_bilan_ishlaydi(self, staff, problem) -> None:
        c = APIClient()
        c.force_authenticate(user=staff)  # sessiya: request.auth = None
        assert c.get(reverse("staff-problem-list")).status_code == 200
