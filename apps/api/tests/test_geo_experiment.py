"""Region A/B (8-qaror, `geoEarlyRegion`) — what it records and how it is read.

Three pieces, measured before the flag was wired (2026-11-10):

- A visitor without a session wrote every event with an EMPTY session key,
  so the funnel's first step counted all of them as one (34 of 38
  `auth.form_started` rows in production were blank). The browser now sends
  a per-tab id and the server files the event under `f:<id>`.
- The dashboard compared raw "done" counts only; it now gives each group's
  started / done / completion and the share of its new accounts that hold a
  region — the point of asking early.
- Group `b` sends the region on the sign-up form, which accepted any text
  there while the settings page refuses anything but a catalogue code.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import AnalyticsEvent, User

FID = "0123456789abcdef0123456789abcdef"


def post_events(client: APIClient, *events: dict[str, Any]) -> Any:
    return client.post("/api/v1/analytics/events/", {"events": list(events)}, format="json")


@pytest.mark.django_db
class TestFunnelId:
    def test_mehmon_hodisasi_tab_id_bilan_yoziladi(self) -> None:
        r = post_events(
            APIClient(), {"name": "auth.form_started", "props": {"mode": "register", "fid": FID}}
        )
        assert r.status_code == 204
        row = AnalyticsEvent.objects.get()
        assert row.session_key == f"f:{FID}"
        # The id names the tab; it is not kept as data.
        assert "fid" not in row.props
        assert row.props == {"mode": "register"}

    def test_ikki_tab_ikki_sessiya(self) -> None:
        other = "f" * 32
        post_events(APIClient(), {"name": "auth.form_started", "props": {"fid": FID}})
        post_events(APIClient(), {"name": "auth.form_started", "props": {"fid": other}})
        keys = set(AnalyticsEvent.objects.values_list("session_key", flat=True))
        assert keys == {f"f:{FID}", f"f:{other}"}

    @pytest.mark.parametrize("bad", ["", "XYZ", FID.upper(), FID + "0", "../../etc", 12345])
    def test_yaroqsiz_id_sessiya_bolmaydi(self, bad: object) -> None:
        post_events(APIClient(), {"name": "auth.form_started", "props": {"fid": bad}})
        row = AnalyticsEvent.objects.get()
        assert row.session_key == ""
        assert "fid" not in row.props

    def test_haqiqiy_sessiya_ustun(self) -> None:
        """A signed-in visitor's events stay under the Django session key."""
        User.objects.create_user("kirgan", password="Parol!12345")
        client = APIClient()
        client.login(username="kirgan", password="Parol!12345")
        post_events(client, {"name": "auth.login_done", "props": {"fid": FID}})
        row = AnalyticsEvent.objects.get()
        assert row.session_key == client.session.session_key
        assert not row.session_key.startswith("f:")


def ab(staff: User) -> Any:
    c = APIClient()
    c.force_authenticate(user=staff)
    return c.get(reverse("staff-analytics")).json()["variant"]


def event(name: str, session: str, user: User | None = None, **props: object) -> None:
    AnalyticsEvent.objects.create(name=name, session_key=session, user=user, props=props)


@pytest.mark.django_db
class TestGroupComparison:
    @pytest.fixture
    def staff(self) -> User:
        return User.objects.create_user("analitik", password="x", is_staff=True)

    def test_guruh_boyicha_boshladi_tugatdi_ulush(self, staff: User) -> None:
        for s in ("a1", "a2", "a3", "a4"):
            event("auth.form_started", f"f:{s}", mode="register", exp="a")
        for s in ("b1", "b2"):
            event("auth.form_started", f"f:{s}", mode="register", exp="b")
        u1 = User.objects.create_user("u1", password="x", country="UZ", region="toshkent")
        u2 = User.objects.create_user("u2", password="x")
        u3 = User.objects.create_user("u3", password="x", country="UZ", region="samarqand")
        event("auth.register_done", "s-u1", u1, exp="a")
        event("auth.register_done", "s-u2", u2, exp="a")
        event("auth.register_done", "s-u3", u3, exp="b")

        groups = ab(staff)["groups"]
        assert groups["a"] == {"started": 4, "done": 2, "completion": 50.0, "region_filled": 50.0}
        assert groups["b"] == {"started": 2, "done": 1, "completion": 50.0, "region_filled": 100.0}

    def test_kirish_formasi_sinovga_kirmaydi(self, staff: User) -> None:
        """`auth.form_started` comes from the sign-in form too."""
        event("auth.form_started", "f:x", mode="login", exp="b")
        assert ab(staff)["groups"]["b"]["started"] == 0

    def test_guruhsiz_va_bosh_sessiya_sanalmaydi(self, staff: User) -> None:
        event("auth.form_started", "f:x", mode="register")  # experiment off: no tag
        event("auth.form_started", "", mode="register", exp="a")  # old blank key
        assert ab(staff)["groups"]["a"]["started"] == 0

    def test_eski_kalitlar_saqlanadi(self, staff: User) -> None:
        """The admin page and older clients still read these."""
        data = ab(staff)
        assert {"control", "variant", "total", "control_share", "groups"} <= set(data)


@pytest.mark.django_db
class TestRegionOnSignUp:
    URL = "/api/v1/auth/register/"

    def _post(self, **over: object) -> Any:
        data = {
            "email": "viloyat@example.uz",
            "first_name": "Ali",
            "last_name": "Valiyev",
            "password": "Kuchli!Parol9",
            "terms_accepted": True,
            **over,
        }
        return APIClient().post(self.URL, data, format="json")

    def test_katalog_kodi_saqlanadi(self) -> None:
        assert self._post(country="UZ", region="samarqand").status_code == 201
        user = User.objects.get(email="viloyat@example.uz")
        assert (user.country, user.region) == ("UZ", "samarqand")

    def test_katalogda_yoq_viloyat_rad_etiladi(self) -> None:
        r = self._post(country="UZ", region="Atlantida")
        assert r.status_code == 400
        assert "region" in r.json()["error"]["details"]
        assert not User.objects.filter(email="viloyat@example.uz").exists()

    def test_viloyatsiz_ham_otadi(self) -> None:
        """Group `a` sends no region at all; it stays optional."""
        assert self._post().status_code == 201
