"""The notification inbox: coded messages, seen vs read, the bell's counts."""

from __future__ import annotations

import re
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from notifications import messages, services
from notifications.message_catalog import CATALOG
from notifications.models import Notification
from notifications.services import notify, notify_many

SLOT = re.compile(r"\{(\w+)\}")


def client_for(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def system(user: User, title: str = "x", **extra: Any) -> Notification:
    row = notify(user, Notification.Kind.SYSTEM, title, **extra)
    assert row is not None
    return row


class TestCatalogue:
    def test_every_language_knows_every_code(self) -> None:
        source = set(CATALOG["uz"])
        assert len(CATALOG) == 10
        for locale, table in CATALOG.items():
            assert set(table) == source, locale

    def test_a_translation_uses_no_slot_the_source_lacks(self) -> None:
        """A slot the sender never fills would reach the reader as `{name}`."""
        for locale, table in CATALOG.items():
            for code, parts in table.items():
                for part, text in parts.items():
                    allowed = set(SLOT.findall(CATALOG["uz"][code].get(part, "")))
                    assert set(SLOT.findall(text)) <= allowed, (locale, code, part)

    def test_a_timestamp_slot_is_shown_as_a_local_time(self) -> None:
        title, body = messages.render(
            "duel_accepted",
            {"user": "ali", "duel": "Kuz", "start_at": "2026-10-06T14:30:00+00:00"},
            "en",
        )
        assert title == "ali accepted your challenge"
        assert "06.10.2026" in body and "T14" not in body

    def test_an_unknown_language_falls_back_to_the_source(self) -> None:
        assert messages.render("streak", {"days": 7}, "xx")[0] == "7 kunlik streak!"

    def test_an_unknown_code_renders_nothing(self) -> None:
        assert messages.render("no_such_code", {}, "uz") == ("", "")


@pytest.mark.django_db
class TestCodedMessages:
    def test_the_stored_text_is_in_the_recipients_language(self, user) -> None:
        User.objects.filter(pk=user.pk).update(locale="ru")
        user.refresh_from_db()
        row = notify(user, Notification.Kind.STREAK_MILESTONE, code="streak", params={"days": 30})
        assert row is not None
        assert row.code == "streak"
        assert row.params == {"days": 30}
        assert row.title == "Серия 30 дней!"

    def test_text_a_person_wrote_wins_over_the_catalogue(self, user) -> None:
        row = notify(
            user,
            Notification.Kind.SYSTEM,
            code="hackathon_scored",
            params={"score": 80},
            body="Yaxshi ish",
        )
        assert row is not None
        assert row.title == "Xakaton bahosi: 80/100"
        assert row.body == "Yaxshi ish"

    def test_every_code_a_sender_uses_is_in_the_catalogue(self) -> None:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        used: set[str] = set()
        for path in root.glob("*/services.py"):
            used |= set(re.findall(r'code="([a-z_]+)"', path.read_text(encoding="utf-8")))
            text = path.read_text(encoding="utf-8")
            used |= set(re.findall(r'Hack\.Status\.\w+: "(hack_[a-z]+)"', text))
            used |= set(re.findall(r'"(duel_(?:draw|won|lost))"', text))
        assert used, "no coded sender found — the pattern above is stale"
        assert used <= messages.codes(), sorted(used - messages.codes())

    def test_the_site_channel_switched_off_writes_no_row(self, user) -> None:
        User.objects.filter(pk=user.pk).update(notify_prefs={"system": {"site": False}})
        user.refresh_from_db()
        assert notify(user, Notification.Kind.SYSTEM, "x") is None
        assert not Notification.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestSeenAndRead:
    def test_opening_the_bell_marks_seen_not_read(self, user) -> None:
        system(user, "a")
        system(user, "b")
        assert services.summary(user) == {"total": 2, "unread": 2, "unseen": 2, "kinds": ["system"]}
        assert services.mark_seen(user) == 2
        assert services.summary(user)["unread"] == 2
        assert services.summary(user)["unseen"] == 0

    def test_a_later_arrival_rings_again(self, user) -> None:
        system(user, "a")
        services.mark_seen(user)
        system(user, "b")
        assert services.summary(user)["unseen"] == 1

    def test_reading_also_marks_seen(self, user) -> None:
        row = system(user)
        services.mark_read(user, [row.pk])
        row.refresh_from_db()
        assert row.read_at is not None and row.seen_at is not None

    def test_unread_again_stays_seen(self, user) -> None:
        row = system(user)
        services.mark_read(user, [row.pk])
        assert services.mark_unread(user, [row.pk]) == 1
        assert services.summary(user)["unread"] == 1
        assert services.summary(user)["unseen"] == 0

    def test_clearing_takes_only_what_was_read(self, user, other_user) -> None:
        read = system(user, "read")
        system(user, "unread")
        theirs = system(other_user, "theirs")
        services.mark_read(user, [read.pk])
        services.mark_read(other_user, [theirs.pk])
        assert services.clear_read(user) == 1
        assert list(Notification.objects.filter(user=user).values_list("title", flat=True)) == [
            "unread"
        ]
        assert Notification.objects.filter(pk=theirs.pk).exists()


@pytest.mark.django_db
class TestApi:
    def test_a_guest_gets_nothing(self) -> None:
        for name in ("notification-list", "notification-summary"):
            assert APIClient().get(reverse(name)).status_code in (401, 403)
        assert APIClient().post(reverse("notification-mark-seen")).status_code in (401, 403)

    def test_the_list_carries_the_code_and_its_values(self, user) -> None:
        notify(user, Notification.Kind.STREAK_MILESTONE, code="streak", params={"days": 7})
        row = client_for(user).get(reverse("notification-list")).json()["results"][0]
        assert row["code"] == "streak"
        assert row["params"] == {"days": 7}
        assert row["is_read"] is False
        assert row["title"] == "7 kunlik streak!"

    def test_filters(self, user) -> None:
        read = system(user, "read")
        system(user, "unread")
        notify(user, Notification.Kind.DUEL, "duel")
        services.mark_read(user, [read.pk])
        client = client_for(user)

        def titles(**params: str) -> list[str]:
            body = client.get(reverse("notification-list"), params).json()
            return sorted(row["title"] for row in body["results"])

        assert titles() == ["duel", "read", "unread"]
        assert titles(unread="true") == ["duel", "unread"]
        assert titles(kind="duel") == ["duel"]
        assert titles(kind="duel,system", unread="true") == ["duel", "unread"]
        # A typo lists nothing — not everything.
        assert titles(kind="duell") == []

    def test_the_list_is_paged(self, user) -> None:
        for n in range(5):
            system(user, f"n{n}")
        client = client_for(user)
        first = client.get(reverse("notification-list"), {"page_size": 2}).json()
        assert len(first["results"]) == 2 and first["next"]
        second = client.get(first["next"]).json()
        assert {row["id"] for row in first["results"]}.isdisjoint(
            row["id"] for row in second["results"]
        )

    def test_summary(self, user) -> None:
        system(user)
        notify(user, Notification.Kind.DUEL, "d")
        body = client_for(user).get(reverse("notification-summary")).json()
        assert body == {"total": 2, "unread": 2, "unseen": 2, "kinds": ["duel", "system"]}

    def test_mark_seen_read_unread(self, user) -> None:
        row = system(user)
        client = client_for(user)
        assert client.post(reverse("notification-mark-seen")).json() == {"updated": 1}
        assert client.post(
            reverse("notification-mark-read"), {"ids": [row.pk]}, format="json"
        ).json() == {"updated": 1}
        assert client.post(
            reverse("notification-mark-unread"), {"ids": [row.pk]}, format="json"
        ).json() == {"updated": 1}
        assert (
            client.post(reverse("notification-mark-unread"), {}, format="json").status_code == 400
        )

    def test_another_users_rows_are_out_of_reach(self, user, other_user) -> None:
        theirs = system(other_user)
        services.mark_read(other_user, [theirs.pk])
        client = client_for(user)
        assert client.post(
            reverse("notification-mark-unread"), {"ids": [theirs.pk]}, format="json"
        ).json() == {"updated": 0}
        assert client.delete(reverse("notification-detail", args=[theirs.pk])).status_code == 404
        assert client.post(reverse("notification-clear-read")).json() == {"updated": 0}
        assert Notification.objects.filter(pk=theirs.pk, read_at__isnull=False).exists()

    def test_delete_one(self, user) -> None:
        row = system(user)
        assert (
            client_for(user).delete(reverse("notification-detail", args=[row.pk])).status_code
            == 204
        )
        assert not Notification.objects.filter(pk=row.pk).exists()


@pytest.mark.django_db
class TestAnnouncement:
    @pytest.fixture
    def published(self, monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str, dict[str, Any]]]:
        from realtime import bus

        sent: list[tuple[str, str, dict[str, Any]]] = []
        monkeypatch.setattr(
            bus, "publish", lambda channel, event, payload: sent.append((channel, event, payload))
        )
        return sent

    def test_a_new_row_is_announced_after_the_commit(
        self, user, published, django_capture_on_commit_callbacks
    ) -> None:
        from realtime import bus

        with django_capture_on_commit_callbacks(execute=True):
            row = system(user)
            assert published == []  # not before the transaction commits
        assert published == [
            (bus.user_channel(user.pk), "notification", {"id": row.pk, "kind": "system"})
        ]

    def test_a_mass_send_does_not_flood_the_bus(
        self, published, django_capture_on_commit_callbacks, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(services, "ANNOUNCE_MAX", 2)
        users = [
            User.objects.create_user(username=f"m{n}", password="Parol!12345") for n in range(3)
        ]
        with django_capture_on_commit_callbacks(execute=True):
            assert notify_many(users, Notification.Kind.SYSTEM, "x") == 3
        assert published == []
        assert Notification.objects.count() == 3

    def test_a_small_group_is_announced(
        self, user, other_user, published, django_capture_on_commit_callbacks
    ) -> None:
        with django_capture_on_commit_callbacks(execute=True):
            notify_many([user, other_user], Notification.Kind.SYSTEM, "x")
        assert len(published) == 2
