"""Account-security notices (decision 2026-11-16).

Seven events that tell a person something happened to their account: a sign-in
from a new device, a changed or reset password, a changed email, a linked
Telegram account, a scheduled or cancelled deletion. They go through the same
`notify` as everything else, in the `security` group: the site channel cannot
be switched off (`groups.MANDATORY`); email and Telegram stay the person's
choice, off by default (2026-11-10).

Each function is safe to call from a request: `notify` swallows its own errors,
and the arguments are plain values the caller already has.
"""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from core.models import User
from notifications.models import Notification
from notifications.services import notify


def _send(user: User, code: str, **params: str) -> None:
    notify(
        user,
        Notification.Kind.SYSTEM,
        code=code,
        params=params,
        ref_type="security",
        ref_id=user.pk,
    )


def new_device(user: User, device: str) -> None:
    _send(user, "security_new_device", device=device)


def password_changed(user: User) -> None:
    _send(user, "security_password_changed")


def password_reset(user: User) -> None:
    _send(user, "security_password_reset")


def email_changed(user: User, new_email: str) -> None:
    _send(user, "security_email_changed", email=new_email)


def telegram_linked(user: User) -> None:
    _send(user, "security_telegram_linked")


def deletion_scheduled(user: User, due: datetime) -> None:
    # The site's own day, as numbers (decision 2026-10-06: dates in the site zone).
    _send(user, "security_deletion_scheduled", date=timezone.localtime(due).strftime("%Y-%m-%d"))


def deletion_cancelled(user: User) -> None:
    _send(user, "security_deletion_cancelled")
