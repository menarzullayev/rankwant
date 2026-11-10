"""Email copy of a notification — the third channel next to the site and Telegram.

Decisions (owner, 2026-11-10; CLAUDE.md row of that day):

* **Opt-in.** Every kind starts off (`services.DEFAULT_CHANNELS`); the
  reader switches a kind on in Settings → Notifications.
* **Personal only.** `services.notify()` copies a notification to email;
  `services.notify_many()` (a new post, a staff broadcast) never does —
  one announcement is ~974k rows and the chain sends 700 mails a day.
* **Verified address only.** An unverified address may be a typo or
  someone else's: a copy of a person's activity must not land there.
* **Five minutes, and only if still unread.** The task is queued with a
  countdown (`EMAIL_DELAY_SECONDS`); when it runs, a row read on the site
  in the meantime is not mailed. Never inside the request.
* **Account mail keeps a reserve.** Password reset and address
  confirmation must not fail because notifications spent the day's quota:
  below `RESERVE_FOR_ACCOUNT_MAIL` left in the chain a notification email
  is skipped (the in-app row stays). A person gets at most
  `PER_USER_DAILY_CAP` notification emails a UTC day.
* **One-click unsubscribe.** Every mail carries signed links (`make_token`)
  that can do one thing only — switch email off, for one kind or all — and
  the RFC 8058 `List-Unsubscribe` / `List-Unsubscribe-Post` headers.
* **The account's language** (`User.locale`); free text a person wrote
  (a staff message, a judge's feedback) stays as written.
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.template.loader import render_to_string

from core import email_text, mail_quota
from core.mailer import is_placeholder, send_email
from core.models import EmailDelivery, User
from notifications.message_catalog import KIND_NAMES
from notifications.models import Notification

log = logging.getLogger(__name__)

#: How long a notification waits before it is mailed. Read on the site in
#: the meantime, it is not mailed at all.
EMAIL_DELAY_SECONDS = 300

#: Mails the chain keeps for password reset and address confirmation. The
#: chain sends 700 a day on free plans (`mail_quota.DAILY_QUOTA`).
RESERVE_FOR_ACCOUNT_MAIL = 200

#: Notification emails one person can receive in a UTC day.
PER_USER_DAILY_CAP = 10

#: An unsubscribe token signed with this salt cannot be replayed as any
#: other signed value of the site (password reset, email change).
UNSUBSCRIBE_SALT = "notifications.email-unsubscribe"

#: The token's kind for "every kind".
ALL_KINDS = "*"


def reachable(user: User) -> bool:
    """Has an address we may write to: active, verified, not a placeholder."""
    return bool(
        user.is_active
        and user.email
        and user.email_verified_at is not None
        and not is_placeholder(user.email)
    )


# ── unsubscribe ──────────────────────────────────────────────────────────


def make_token(user_id: int, kind: str) -> str:
    """A link credential that can only switch email off. It does not expire:
    a mail sits in an inbox for years and its link must keep working."""
    return signing.dumps({"u": user_id, "k": kind}, salt=UNSUBSCRIBE_SALT)


def read_token(token: str) -> tuple[int, str] | None:
    """`(user_id, kind)`, or `None` for anything that is not our token."""
    try:
        data: Any = signing.loads(token, salt=UNSUBSCRIBE_SALT)
    except signing.BadSignature:
        return None
    if not isinstance(data, dict):
        return None
    user_id, kind = data.get("u"), data.get("k")
    if not isinstance(user_id, int) or not isinstance(kind, str):
        return None
    if kind != ALL_KINDS and kind not in Notification.Kind.values:
        return None
    return user_id, kind


def unsubscribe(user: User, kind: str) -> None:
    """Switches email off for one kind, or for every kind with `ALL_KINDS`.

    The other channels of the kind keep their current value, written out
    explicitly so the stored preference does not depend on a default.
    """
    from notifications.services import channels

    kinds = list(Notification.Kind.values) if kind == ALL_KINDS else [kind]
    with transaction.atomic():
        locked = User.objects.select_for_update().get(pk=user.pk)
        prefs = dict(locked.notify_prefs or {})
        for each in kinds:
            current = channels(locked, each)
            prefs[each] = {"site": current.site, "telegram": current.telegram, "email": False}
        locked.notify_prefs = prefs
        locked.save(update_fields=["notify_prefs"])
    user.notify_prefs = prefs


def unsubscribe_links(user_id: int, kind: str) -> dict[str, str]:
    """The page links in the footer and the one-click URL for the header."""
    site = settings.SITE_URL

    def page(for_kind: str) -> str:
        return f"{site}/unsubscribe?{urlencode({'token': make_token(user_id, for_kind)})}"

    one_click = make_token(user_id, kind)
    return {
        "unsubscribe_kind_url": page(kind),
        "unsubscribe_all_url": page(ALL_KINDS),
        "settings_url": f"{site}/settings/bildirishnomalar",
        "one_click_url": (
            f"{site}/api/v1/notifications/unsubscribe/?{urlencode({'token': one_click})}"
        ),
    }


# ── the mail ─────────────────────────────────────────────────────────────


def render(user: User, kind: str, title: str, body: str) -> dict[str, Any]:
    """Subject, both bodies and the headers of one notification email."""
    locale = user.locale or email_text.DEFAULT_LOCALE
    t = {
        **email_text.strings(email_text.SHARED, locale),
        **email_text.strings(email_text.NOTIFY, locale),
    }
    names = KIND_NAMES.get(locale) or KIND_NAMES[email_text.DEFAULT_LOCALE]
    t["footer"] = t["footer"].replace("{kind}", names.get(kind, kind))
    t["heading"] = title
    t["body"] = body
    t["subject"] = f"{t['brand']} — {title}"[:200]
    links = unsubscribe_links(user.pk, kind)
    context = {
        "t": t,
        "locale": locale,
        "code": "",
        "link": f"{settings.SITE_URL}/notifications",
        "site_url": settings.SITE_URL,
        "site_host": urlsplit(settings.SITE_URL).netloc,
        "request_at": "",
        **links,
    }
    return {
        "subject": t["subject"],
        "text": render_to_string("email/base.txt", context),
        "html": render_to_string("email/base.html", context),
        "headers": {
            "List-Unsubscribe": f"<{links['one_click_url']}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    }


def budget_refusal(user: User) -> str:
    """Why this mail may not go now, or `""` when it may."""
    sent_today = EmailDelivery.objects.filter(
        purpose=EmailDelivery.Purpose.NOTIFICATION,
        status=EmailDelivery.Status.SENT,
        to_email=user.email,
        created_at__gte=mail_quota.day_start(),
    ).count()
    if sent_today >= PER_USER_DAILY_CAP:
        return "per_user_cap"
    left = mail_quota.chain_remaining()
    if left is not None and left <= RESERVE_FOR_ACCOUNT_MAIL:
        return "reserve"
    return ""


#: What a skip says in `EmailDelivery.attempts` — for whoever opens the row
#: in the admin to answer "why did no email come".
SKIP_DETAIL = {
    "per_user_cap": f"bildirishnoma: kunlik {PER_USER_DAILY_CAP} ta xat chegarasi",
    "reserve": f"bildirishnoma: {RESERVE_FOR_ACCOUNT_MAIL} ta xat hisob xatlari uchun zaxirada",
}


def deliver(*, user_id: int, kind: str, title: str, body: str, notification_id: int | None) -> str:
    """Sends one notification email, or says why not. Never raises."""
    from notifications.services import channels

    user = User.objects.filter(pk=user_id).first()
    if user is None or not reachable(user):
        return "skipped:unreachable"
    if not channels(user, kind).email:
        return "skipped:off"
    if notification_id is not None:
        row = Notification.objects.filter(pk=notification_id, user=user).values("read_at").first()
        if row is None:
            return "skipped:deleted"
        if row["read_at"] is not None:
            return "skipped:read"

    refusal = budget_refusal(user)
    if refusal:
        EmailDelivery.objects.create(
            to_email=user.email[:254],
            purpose=EmailDelivery.Purpose.NOTIFICATION,
            subject=title[:200],
            status=EmailDelivery.Status.SKIPPED,
            attempts=[{"provider": "", "error": SKIP_DETAIL[refusal]}],
        )
        log.info("bildirishnoma xati o'tkazib yuborildi (%s): %s", refusal, user.pk)
        return f"skipped:{refusal}"

    mail = render(user, kind, title, body)

    delivery = send_email(
        to=user.email,
        subject=mail["subject"],
        text=mail["text"],
        html=mail["html"],
        purpose=EmailDelivery.Purpose.NOTIFICATION,
        headers=mail["headers"],
    )
    return str(delivery.status)


def schedule(user: User, kind: str, title: str, body: str, notification_id: int | None) -> None:
    """Queues the mail after the surrounding transaction commits.

    Before the commit the row may still roll back (a duel that failed to
    start) — a mail about it must not go. A broker that is down loses the
    mail, not the action that caused it.
    """
    if not reachable(user):
        return
    kwargs = {
        "user_id": user.pk,
        "kind": kind,
        "title": title,
        "body": body,
        "notification_id": notification_id,
    }

    def push() -> None:
        from notifications.tasks import send_notification_email

        try:
            send_notification_email.apply_async(kwargs=kwargs, countdown=EMAIL_DELAY_SECONDS)
        except Exception:
            log.warning("bildirishnoma xati navbatga qo'yilmadi: %s", user.pk, exc_info=True)

    transaction.on_commit(push)
