"""Email copy of a notification — owner decisions of 2026-11-10 (`notifications.email`).

Opt-in per kind, personal notifications only, verified addresses only,
sent five minutes later unless read, a reserve kept for account mail, a
per-user daily cap, a signed one-click unsubscribe, the account's language.
No test reaches a provider: the chain is replaced with fakes.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.core import signing
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from core import mail_quota
from core.mail_providers import Brevo, MailerSend, Message, SendError
from core.models import EmailDelivery, User
from notifications import email as email_channel
from notifications.models import Notification
from notifications.services import channels, notify, notify_many

UNSUBSCRIBE_URL = "/api/v1/notifications/unsubscribe/"


class FakeProvider:
    def __init__(self, name: str, *, ok: bool = True) -> None:
        self.name = name
        self.ok = ok
        self.configured = True
        self.calls: list[Message] = []

    def send(self, msg: Message) -> None:
        self.calls.append(msg)
        if not self.ok:
            raise SendError("HTTP 429")


@pytest.fixture
def brevo(monkeypatch: pytest.MonkeyPatch):
    fake = FakeProvider("brevo")
    providers = {"brevo": fake}
    monkeypatch.setattr("core.mailer.PROVIDERS", providers)
    monkeypatch.setattr("core.mail_providers.PROVIDERS", providers)
    with override_settings(EMAIL_CHAIN=["brevo"], SITE_URL="https://rankwant.uz"):
        yield fake


@pytest.fixture
def queued(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """What `schedule()` handed to Celery, with its countdown — not run."""
    calls: list[dict[str, Any]] = []

    def apply_async(*, kwargs: dict[str, Any], countdown: int) -> None:
        calls.append({**kwargs, "countdown": countdown})

    monkeypatch.setattr("notifications.tasks.send_notification_email.apply_async", apply_async)
    return calls


def _reader(username: str = "nodira", *, verified: bool = True, **prefs: bool) -> User:
    user = User.objects.create_user(
        username=username,
        password="Parol!12345",
        email=f"{username}@rankwant.uz",
    )
    user.email_verified_at = timezone.now() if verified else None
    if prefs:
        user.notify_prefs = {"duel": {"site": True, "telegram": False, **prefs}}
    user.save()
    return user


def _notify(user: User, capture: Any) -> Notification | None:
    with capture(execute=True):
        return notify(
            user,
            Notification.Kind.DUEL,
            code="duel_cancelled",
            params={"duel": "Kechki duel"},
            ref_type="duel",
            ref_id="kechki",
        )


@pytest.mark.django_db
class TestOptIn:
    def test_email_is_off_by_default(self, queued, django_capture_on_commit_callbacks) -> None:
        user = _reader()
        assert channels(user, Notification.Kind.DUEL).email is False
        _notify(user, django_capture_on_commit_callbacks)
        assert queued == []

    def test_switched_on_it_is_queued_five_minutes_later(
        self, queued, django_capture_on_commit_callbacks
    ) -> None:
        user = _reader(email=True)
        row = _notify(user, django_capture_on_commit_callbacks)
        assert row is not None
        assert len(queued) == 1
        assert queued[0]["countdown"] == email_channel.EMAIL_DELAY_SECONDS == 300
        assert queued[0]["notification_id"] == row.pk
        assert queued[0]["kind"] == Notification.Kind.DUEL

    def test_unverified_address_gets_nothing(
        self, queued, django_capture_on_commit_callbacks
    ) -> None:
        user = _reader(verified=False, email=True)
        _notify(user, django_capture_on_commit_callbacks)
        assert queued == []

    def test_bulk_announcement_never_goes_by_email(
        self, queued, django_capture_on_commit_callbacks
    ) -> None:
        user = _reader(email=True)
        user.notify_prefs = {"system": {"site": True, "email": True}}
        user.save()
        with django_capture_on_commit_callbacks(execute=True):
            assert notify_many([user], Notification.Kind.SYSTEM, "Yangi post") == 1
        assert queued == []

    def test_nothing_is_queued_before_the_commit(self, queued) -> None:
        """A rolled-back event must not be mailed: queueing waits for the commit."""
        user = _reader(email=True)
        notify(user, Notification.Kind.DUEL, "x")
        assert queued == []

    def test_site_off_still_mails_without_a_row(
        self, queued, django_capture_on_commit_callbacks
    ) -> None:
        user = _reader()
        user.notify_prefs = {"duel": {"site": False, "email": True}}
        user.save()
        assert _notify(user, django_capture_on_commit_callbacks) is None
        assert queued[0]["notification_id"] is None


@pytest.mark.django_db
class TestDeliver:
    def _deliver(self, user: User, row: Notification | None = None) -> str:
        return email_channel.deliver(
            user_id=user.pk,
            kind=Notification.Kind.DUEL,
            title="Duel bekor qilindi: Kechki duel",
            body="",
            notification_id=row.pk if row else None,
        )

    def test_sends_with_one_click_headers(self, brevo) -> None:
        user = _reader(email=True)
        assert self._deliver(user) == EmailDelivery.Status.SENT
        [msg] = brevo.calls
        assert msg.to == user.email
        assert msg.subject == "RankWant — Duel bekor qilindi: Kechki duel"
        assert msg.headers["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
        header = msg.headers["List-Unsubscribe"]
        assert header.startswith(f"<https://rankwant.uz{UNSUBSCRIBE_URL}?token=")
        assert "/unsubscribe?token=" in msg.text
        assert "Bu turdagi xatlarni o'chirish" in msg.text and "&#x27;" not in msg.text
        assert "https://rankwant.uz/settings/bildirishnomalar" in msg.html
        row = EmailDelivery.objects.get()
        assert row.purpose == EmailDelivery.Purpose.NOTIFICATION

    def test_read_on_the_site_is_not_mailed(self, brevo) -> None:
        user = _reader(email=True)
        row = Notification.objects.create(user=user, kind="duel", title="x", read_at=timezone.now())
        assert self._deliver(user, row) == "skipped:read"
        assert brevo.calls == [] and not EmailDelivery.objects.exists()

    def test_deleted_row_is_not_mailed(self, brevo) -> None:
        user = _reader(email=True)
        row = Notification.objects.create(user=user, kind="duel", title="x")
        row.delete()
        row.pk = 999_999
        assert self._deliver(user, row) == "skipped:deleted"

    def test_switched_off_meanwhile_is_not_mailed(self, brevo) -> None:
        user = _reader(email=True)
        user.notify_prefs = {"duel": {"email": False}}
        user.save()
        assert self._deliver(user) == "skipped:off"
        assert brevo.calls == []

    def test_per_user_daily_cap(self, brevo) -> None:
        user = _reader(email=True)
        EmailDelivery.objects.bulk_create(
            EmailDelivery(
                to_email=user.email,
                purpose=EmailDelivery.Purpose.NOTIFICATION,
                subject="x",
                status=EmailDelivery.Status.SENT,
                provider="brevo",
            )
            for _ in range(email_channel.PER_USER_DAILY_CAP)
        )
        assert self._deliver(user) == "skipped:per_user_cap"
        assert brevo.calls == []
        skipped = EmailDelivery.objects.get(status=EmailDelivery.Status.SKIPPED)
        assert "chegarasi" in skipped.attempts[0]["error"]

    def test_account_mail_keeps_its_reserve(self, brevo, monkeypatch) -> None:
        user = _reader(email=True)
        monkeypatch.setattr(
            mail_quota, "chain_remaining", lambda: email_channel.RESERVE_FOR_ACCOUNT_MAIL
        )
        assert self._deliver(user) == "skipped:reserve"
        assert brevo.calls == []
        monkeypatch.setattr(
            mail_quota, "chain_remaining", lambda: email_channel.RESERVE_FOR_ACCOUNT_MAIL + 1
        )
        assert self._deliver(user) == EmailDelivery.Status.SENT

    def test_written_in_the_accounts_language(self, brevo) -> None:
        user = _reader(email=True)
        user.locale = "ru"
        user.save()
        self._deliver(user)
        text = brevo.calls[0].text
        assert "Отключить письма этого типа" in text
        assert "«Дуэли»" in text


@pytest.mark.django_db
class TestChainRemaining:
    def test_counts_configured_chain_only(self, brevo) -> None:
        assert mail_quota.chain_remaining() == mail_quota.DAILY_QUOTA["brevo"]

    def test_unmetered_console_never_runs_out(self, monkeypatch) -> None:
        console = FakeProvider("console")
        monkeypatch.setattr("core.mail_providers.PROVIDERS", {"console": console})
        with override_settings(EMAIL_CHAIN=["console"]):
            assert mail_quota.chain_remaining() is None


class TestProviders:
    def test_brevo_forwards_the_headers_mailersend_does_not(self, monkeypatch, settings) -> None:
        sent: list[dict[str, Any]] = []

        def post(url: str, payload: dict[str, Any], headers: dict[str, str]) -> str:
            sent.append(payload)
            return "{}"

        monkeypatch.setattr("core.mail_providers._post", post)
        settings.BREVO_API_KEY = settings.MAILERSEND_API_KEY = "k"
        msg = Message(
            to="a@rankwant.uz", subject="s", text="t", headers={"List-Unsubscribe": "<u>"}
        )
        Brevo().send(msg)
        MailerSend().send(msg)
        assert sent[0]["headers"] == {"List-Unsubscribe": "<u>"}
        assert "headers" not in sent[1]


@pytest.mark.django_db
class TestUnsubscribe:
    def test_token_round_trip_and_forgeries(self) -> None:
        token = email_channel.make_token(7, "duel")
        assert email_channel.read_token(token) == (7, "duel")
        assert email_channel.read_token(token + "x") is None
        # Another salt: a different signed value of the site cannot be replayed.
        other = signing.dumps({"u": 7, "k": "duel"}, salt="core.password-reset")
        assert email_channel.read_token(other) is None
        bogus = signing.dumps({"u": 7, "k": "nope"}, salt=email_channel.UNSUBSCRIBE_SALT)
        assert email_channel.read_token(bogus) is None

    def test_get_only_reads(self) -> None:
        user = _reader(email=True)
        token = email_channel.make_token(user.pk, "duel")
        res = APIClient().get(UNSUBSCRIBE_URL, {"token": token})
        assert res.status_code == 200 and res.json() == {"kind": "duel", "done": False}
        user.refresh_from_db()
        assert channels(user, "duel").email is True

    def test_one_click_post_from_a_mail_client(self) -> None:
        """RFC 8058: form body `List-Unsubscribe=One-Click`, token in the URL,
        no cookie and no CSRF token."""
        user = _reader(email=True)
        token = email_channel.make_token(user.pk, "duel")
        client = APIClient(enforce_csrf_checks=True)
        res = client.post(
            f"{UNSUBSCRIBE_URL}?token={token}",
            "List-Unsubscribe=One-Click",
            content_type="application/x-www-form-urlencoded",
        )
        assert res.status_code == 200 and res.json() == {"kind": "duel", "done": True}
        user.refresh_from_db()
        assert channels(user, "duel") == (True, False, False)

    def test_all_kinds_from_the_page(self) -> None:
        user = _reader(email=True)
        token = email_channel.make_token(user.pk, email_channel.ALL_KINDS)
        res = APIClient().post(UNSUBSCRIBE_URL, {"token": token}, format="json")
        assert res.status_code == 200
        user.refresh_from_db()
        assert not any(channels(user, kind).email for kind in Notification.Kind.values)
        assert all(channels(user, kind).site for kind in Notification.Kind.values)

    @pytest.mark.parametrize("token", ["", "garbage", "a:b:c"])
    def test_bad_link_is_refused(self, token: str) -> None:
        assert APIClient().post(UNSUBSCRIBE_URL, {"token": token}, format="json").status_code == 400
        assert APIClient().get(UNSUBSCRIBE_URL, {"token": token}).status_code == 400


@pytest.mark.django_db
class TestPreferences:
    def test_email_channel_can_be_saved(self) -> None:
        user = _reader()
        client = APIClient()
        client.force_authenticate(user)
        res = client.patch(
            "/api/v1/me/",
            {"notify_prefs": {"duel": {"site": True, "telegram": False, "email": True}}},
            format="json",
        )
        assert res.status_code == 200, res.content
        user.refresh_from_db()
        assert channels(user, "duel").email is True

    def test_unknown_channel_is_refused(self) -> None:
        user = _reader()
        client = APIClient()
        client.force_authenticate(user)
        res = client.patch("/api/v1/me/", {"notify_prefs": {"duel": {"sms": True}}}, format="json")
        assert res.status_code == 400
