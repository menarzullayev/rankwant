"""Notification groups, security notices and timed reminders (decision 2026-11-16)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from contests import reminders as contest_reminders
from contests.models import Contest, ContestRegistration
from core import devices
from core.models import KnownDevice, User
from notifications import groups, message_catalog, reminders
from notifications.models import Notification, ReminderSent
from notifications.services import channels


@pytest.fixture
def person(db) -> User:
    return User.objects.create_user(username="dilnoza", password="Parol!12345", email="d@rw.uz")


def _codes(person: User) -> set[str]:
    return set(Notification.objects.filter(user=person).values_list("code", flat=True))


class TestGroups:
    def test_every_catalogue_code_has_a_group(self) -> None:
        listed = set(message_catalog.CATALOG["en"])
        assert listed - set(groups.CODE_GROUP) == set(), "a code without a settings group"
        assert set(groups.CODE_GROUP) - listed == set(), "a grouped code the catalogue lacks"

    def test_groups_are_known_and_dormant_codes_exist(self) -> None:
        assert set(groups.CODE_GROUP.values()) <= set(groups.GROUPS)
        assert groups.DORMANT <= set(groups.CODE_GROUP)

    def test_a_group_with_only_dormant_codes_is_hidden(self) -> None:
        visible = groups.visible_groups()
        assert "team_prizes" not in visible
        assert "security" in visible and "plan_limits" in visible

    def test_unlisted_code_falls_back_to_its_kind(self) -> None:
        assert groups.group_of("a_future_code", "duel") == "competition"
        assert groups.group_of("a_future_code", "unheard-of") == "community"

    def test_legacy_kind_preference_still_applies(self, person: User) -> None:
        person.notify_prefs = {"duel": {"site": False}}
        assert channels(person, "duel", "duel_won").site is False

    def test_group_preference_wins_over_the_legacy_kind(self, person: User) -> None:
        person.notify_prefs = {"duel": {"site": False}, "competition": {"site": True}}
        assert channels(person, "duel", "duel_won").site is True

    def test_security_site_channel_cannot_be_switched_off(self, person: User) -> None:
        person.notify_prefs = {"security": {"site": False, "email": False}}
        got = channels(person, "system", "security_password_changed")
        assert got.site is True
        assert got.email is False and got.telegram is False

    def test_settings_accept_groups_and_legacy_kinds_only(self, person: User) -> None:
        api = APIClient()
        api.force_authenticate(person)
        ok = api.patch("/api/v1/me/", {"notify_prefs": {"contest": {"email": True}}}, format="json")
        assert ok.status_code == 200
        legacy = api.patch("/api/v1/me/", {"notify_prefs": {"duel": {"site": True}}}, format="json")
        assert legacy.status_code == 200
        bad = api.patch(
            "/api/v1/me/", {"notify_prefs": {"no_such_group": {"site": True}}}, format="json"
        )
        assert bad.status_code == 400


class TestSecurityNotices:
    def test_password_change_notifies_through_the_api(self, person: User) -> None:
        api = APIClient()
        api.force_authenticate(person)
        done = api.post(
            "/api/v1/me/password/",
            {"old_password": "Parol!12345", "new_password": "Yangi!Parol98"},
            format="json",
        )
        assert done.status_code == 204, done.content
        assert "security_password_changed" in _codes(person)

    def test_deletion_scheduled_and_cancelled(self, person: User) -> None:
        from core import account

        account.schedule_deletion(person)
        account.schedule_deletion(person)  # asking again must not notify again
        account.cancel_deletion(person)
        rows = Notification.objects.filter(user=person, code__startswith="security_deletion")
        assert sorted(rows.values_list("code", flat=True)) == [
            "security_deletion_cancelled",
            "security_deletion_scheduled",
        ]
        scheduled = rows.get(code="security_deletion_scheduled")
        assert scheduled.params["date"].count("-") == 2

    def test_security_notice_is_stored_even_when_the_person_muted_the_kind(
        self, person: User
    ) -> None:
        person.notify_prefs = {"security": {"site": False}, "system": {"site": False}}
        person.save()
        from notifications import security

        security.password_changed(person)
        assert "security_password_changed" in _codes(person)


class TestNewDevice:
    CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    CHROME_NEWER = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    PHONE = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/131.0 Mobile Safari/537.36"

    def test_label_names_browser_and_system(self) -> None:
        assert devices.label(self.CHROME) == "Chrome · Windows"
        assert devices.label(self.PHONE) == "Chrome · Android"
        assert devices.label("curl/8.0") == ""

    def test_first_device_is_silent_a_new_one_is_not(self, person: User) -> None:
        devices.note_sign_in(person, self.CHROME)
        assert "security_new_device" not in _codes(person)
        devices.note_sign_in(person, self.PHONE)
        assert "security_new_device" in _codes(person)
        assert KnownDevice.objects.filter(user=person).count() == 2

    def test_a_browser_update_is_not_a_new_device(self, person: User) -> None:
        devices.note_sign_in(person, self.CHROME)
        devices.note_sign_in(person, self.CHROME_NEWER)
        assert "security_new_device" not in _codes(person)

    def test_the_same_new_device_warns_once(self, person: User) -> None:
        devices.note_sign_in(person, self.CHROME)
        devices.note_sign_in(person, self.PHONE)
        devices.note_sign_in(person, self.PHONE)
        assert Notification.objects.filter(user=person, code="security_new_device").count() == 1


def _at(day: date, hour: int, minute: int = 0) -> datetime:
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


def _contest(start_in: timedelta, *, hosts: list[User] | None = None, **fields: Any) -> Contest:
    now = timezone.now()
    contest = Contest.objects.create(
        slug=f"c-{start_in.total_seconds():.0f}",
        title="Kuz kubogi",
        start_at=now + start_in,
        end_at=now + start_in + timedelta(hours=2),
        **fields,
    )
    for host in hosts or []:
        contest.organizers.add(host)
    return contest


class TestReminders:
    def test_registered_person_gets_a_day_and_an_hour_notice_once(self, person: User) -> None:
        day = _contest(timedelta(hours=24))
        hour = _contest(timedelta(hours=1))
        for contest in (day, hour):
            ContestRegistration.objects.create(contest=contest, user=person)
        contest_reminders.run()
        contest_reminders.run()  # a second look must not repeat anything
        assert Notification.objects.filter(user=person, code="contest_starts_in_day").count() == 1
        assert Notification.objects.filter(user=person, code="contest_starts_in_hour").count() == 1

    def test_unregistered_person_gets_nothing(self, person: User) -> None:
        _contest(timedelta(hours=1))
        contest_reminders.run()
        assert Notification.objects.filter(user=person).count() == 0

    def test_a_reminder_is_not_repeated_when_the_site_row_was_deleted(self, person: User) -> None:
        contest = _contest(timedelta(hours=1))
        ContestRegistration.objects.create(contest=contest, user=person)
        contest_reminders.run()
        Notification.objects.filter(user=person).delete()
        contest_reminders.run()
        assert Notification.objects.filter(user=person).count() == 0
        assert ReminderSent.objects.filter(user=person).count() == 1

    def test_host_hears_about_the_hour_and_the_end(self, person: User) -> None:
        soon = _contest(timedelta(hours=1), hosts=[person])
        contest_reminders.run()
        assert "host_contest_starts_in_hour" in _codes(person)
        Contest.objects.filter(pk=soon.pk).update(
            start_at=timezone.now() - timedelta(hours=3), end_at=timezone.now() - timedelta(hours=1)
        )
        contest_reminders.run()
        assert "host_contest_ended" in _codes(person)

    def test_streak_warning_waits_for_the_evening(self, person: User) -> None:
        today = timezone.localdate()
        User.objects.filter(pk=person.pk).update(
            last_active_date=today - timedelta(days=1), streak_count=5
        )
        morning = _at(today, 9)
        evening = _at(today, 20, 5)
        reminders.streak_at_risk(morning)
        assert "streak_at_risk" not in _codes(person)
        reminders.streak_at_risk(evening)
        reminders.streak_at_risk(evening)
        assert Notification.objects.filter(user=person, code="streak_at_risk").count() == 1

    def test_short_streaks_and_frozen_streaks_are_left_alone(self, person: User) -> None:
        today = timezone.localdate()
        User.objects.filter(pk=person.pk).update(
            last_active_date=today - timedelta(days=1), streak_count=1
        )
        evening = _at(today, 21)
        reminders.streak_at_risk(evening)
        User.objects.filter(pk=person.pk).update(streak_count=6, streak_freeze_until=today)
        reminders.streak_at_risk(evening)
        assert _codes(person) == set()

    def test_a_broken_streak_is_announced_once(self, person: User) -> None:
        today = timezone.localdate()
        User.objects.filter(pk=person.pk).update(
            last_active_date=today - timedelta(days=2), streak_count=7
        )
        reminders.streak_broken()
        reminders.streak_broken()
        row = Notification.objects.get(user=person, code="streak_broken")
        assert row.params["days"] == "7"

    def test_old_dedupe_rows_are_pruned(self, person: User) -> None:
        old = ReminderSent.objects.create(user=person, code="x", ref="1")
        ReminderSent.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=90)
        )
        ReminderSent.objects.create(user=person, code="x", ref="2")
        assert reminders.prune() == 1


class TestUnsubscribeByGroup:
    def test_a_group_link_switches_that_groups_email_off(self, person: User) -> None:
        from notifications import email as email_channel

        person.notify_prefs = {"contest": {"email": True, "site": True}}
        person.save()
        email_channel.unsubscribe(person, "contest")
        assert channels(person, "system", "contest_announcement").email is False
        assert email_channel.read_token(email_channel.make_token(person.pk, "contest")) == (
            person.pk,
            "contest",
        )

    def test_unsubscribe_all_keeps_the_security_site_notice(self, person: User) -> None:
        from notifications import email as email_channel

        email_channel.unsubscribe(person, email_channel.ALL_KINDS)
        got = channels(person, "system", "security_password_changed")
        assert got.site is True and got.email is False

    def test_an_old_kind_link_beats_a_group_saved_later(self, person: User) -> None:
        from notifications import email as email_channel

        person.notify_prefs = {"competition": {"email": True}}
        person.save()
        email_channel.unsubscribe(person, "duel")
        assert channels(person, "duel", "duel_won").email is False

    def test_channels_merge_per_channel_across_group_and_kind(self, person: User) -> None:
        person.notify_prefs = {"duel": {"site": False}, "competition": {"email": True}}
        got = channels(person, "duel", "duel_won")
        assert got.site is False and got.email is True


class TestSchedulingGuards:
    def test_a_draft_contest_notifies_nobody(self, person: User) -> None:
        draft = _contest(timedelta(hours=1), hosts=[person], is_public=False)
        ContestRegistration.objects.create(contest=draft, user=person)
        contest_reminders.run()
        assert _codes(person) == set()

    def test_the_streak_scan_runs_once_a_day(self, person: User) -> None:
        from django.core.cache import cache

        cache.clear()
        today = timezone.localdate()
        User.objects.filter(pk=person.pk).update(
            last_active_date=today - timedelta(days=1), streak_count=4
        )
        evening = _at(today, 20, 30)
        assert reminders.run(evening)["streak_at_risk"] == 1
        Notification.objects.filter(user=person).delete()
        ReminderSent.objects.filter(user=person).delete()
        assert "streak_at_risk" not in reminders.run(evening)  # the day's scan is done
        cache.clear()
        assert reminders.run(evening)["streak_at_risk"] == 1


class TestDevicesAreAccountData:
    def test_anonymising_erases_and_the_export_lists_them(self, person: User) -> None:
        from core import account

        devices.note_sign_in(person, TestNewDevice.CHROME)
        exported = account.export(person)
        assert exported["known_devices"][0]["label"] == "Chrome · Windows"
        account.anonymize(person)
        assert KnownDevice.objects.filter(user=person).count() == 0
