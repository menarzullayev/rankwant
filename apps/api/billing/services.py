"""Orders, subscriptions and what a paid order opens (ADR-0057).

`fulfil` and `revoke` are the only two ways access changes; both providers
call them, so Payme and Click cannot disagree about what a payment buys.
"""

from __future__ import annotations

import base64
import calendar
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

from billing.models import RANK, Order, Plan, PlanPrice, Subscription
from core.models import User
from courses import services as courses

log = logging.getLogger(__name__)

#: `courses.Enrollment.Source.PURCHASE`, by value: billing does not import
#: another app's models.
PURCHASED = "purchase"


class BillingError(APIException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    default_code = "billing_refused"
    default_detail = "This purchase is not possible."


def billing_error(
    code: str, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST
) -> BillingError:
    # `core.errors` reads the code from `default_code`, so set it per error.
    err = BillingError(detail=detail, code=code)
    err.status_code = status_code
    err.default_code = code
    return err


# ── Providers ─────────────────────────────────────────────────────────


def providers() -> list[str]:
    """Providers whose merchant settings are present; nothing else is offered."""
    found = []
    if settings.CLICK_SERVICE_ID and settings.CLICK_MERCHANT_ID and settings.CLICK_SECRET_KEY:
        found.append(Order.Provider.CLICK.value)
    if settings.PAYME_MERCHANT_ID and settings.PAYME_KEY:
        found.append(Order.Provider.PAYME.value)
    return found


def return_url(order: Order) -> str:
    return f"{settings.SITE_URL}/billing/return?order={order.pk}"


def pay_url(order: Order, locale: str = "uz") -> str:
    """Where the buyer goes to pay: the provider's own page."""
    if order.provider == Order.Provider.PAYME:
        lang = locale if locale in ("uz", "ru", "en") else "uz"
        params = ";".join(
            [
                f"m={settings.PAYME_MERCHANT_ID}",
                f"ac.order_id={order.pk}",
                f"a={order.amount_uzs * 100}",
                f"l={lang}",
                f"c={return_url(order)}",
            ]
        )
        encoded = base64.b64encode(params.encode()).decode()
        return f"{settings.PAYME_CHECKOUT_URL.rstrip('/')}/{encoded}"
    query = {
        "service_id": settings.CLICK_SERVICE_ID,
        "merchant_id": settings.CLICK_MERCHANT_ID,
        "amount": f"{Decimal(order.amount_uzs):.2f}",
        "transaction_param": str(order.pk),
        "return_url": return_url(order),
    }
    if settings.CLICK_MERCHANT_USER_ID:
        query["merchant_user_id"] = settings.CLICK_MERCHANT_USER_ID
    return f"https://my.click.uz/services/pay/?{urlencode(query)}"


# ── Orders ────────────────────────────────────────────────────────────


def _check_provider(provider: str) -> None:
    if provider not in providers():
        raise billing_error(
            "billing_provider_unavailable",
            "This payment method is not available.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def price_for(plan_code: str, months: int) -> PlanPrice | None:
    return (
        PlanPrice.objects.filter(plan__code=plan_code, plan__is_on_sale=True, months=months)
        .select_related("plan")
        .first()
    )


def create_plan_order(user: User, plan_code: str, months: int, provider: str) -> Order:
    _check_provider(provider)
    price = price_for(plan_code, months)
    if price is None:
        raise billing_error("billing_not_on_sale", "This plan and period are not on sale.")
    return Order.objects.create(
        user=user,
        kind=Order.Kind.PLAN,
        plan=plan_code,
        months=months,
        amount_uzs=price.amount_uzs,
        provider=provider,
    )


def create_course_order(user: User, course: Any, provider: str) -> Order:
    _check_provider(provider)
    if not course.is_published or course.access != course.Access.PAID or course.price_uzs <= 0:
        raise billing_error("billing_not_on_sale", "This course is not sold.")
    if user.enrollments.filter(course=course, source=PURCHASED).exists():
        raise billing_error(
            "billing_already_owned", "You already own this course.", status.HTTP_409_CONFLICT
        )
    return Order.objects.create(
        user=user,
        kind=Order.Kind.COURSE,
        course=course,
        amount_uzs=course.price_uzs,
        provider=provider,
    )


def in_flight(order: Order) -> bool:
    """A provider is mid-payment: Payme holds a created transaction, or Click
    has prepared one (after a successful Prepare and debit, Click's Complete
    must not be refused)."""
    return (
        order.payme_transactions.filter(state=1).exists()
        or order.click_transactions.filter(status="prepared").exists()
    )


def abandon(order: Order) -> bool:
    """The buyer, or the expiry task, gives up an unpaid order. Refused while
    a provider is mid-payment: that payment decides the order."""
    if in_flight(order):
        return False
    return cancel_pending(order)


def cancel_pending(order: Order) -> bool:
    """Cancel an unpaid order (provider callbacks); False if it was no longer pending."""
    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.status != Order.Status.PENDING:
            return False
        locked.status = Order.Status.CANCELLED
        locked.cancelled_at = timezone.now()
        locked.save(update_fields=["status", "cancelled_at"])
    return True


# ── Periods ───────────────────────────────────────────────────────────


def add_months(moment: datetime, months: int) -> datetime:
    """Calendar months: 31 January + 1 month is the last day of February."""
    year, month0 = divmod(moment.month - 1 + months, 12)
    year += moment.year
    day = min(moment.day, calendar.monthrange(year, month0 + 1)[1])
    return moment.replace(year=year, month=month0 + 1, day=day)


def _live(user: User) -> list[Subscription]:
    now = timezone.now()
    return list(user.subscriptions.filter(revoked_at__isnull=True, ends_at__gt=now))


def period_start(user: User, plan_code: str) -> datetime:
    """When a new period of `plan_code` begins.

    The same plan, or a higher one, already paid for runs first: buying Pro
    twice stacks, and Plus bought during Pro waits for Pro to end. A higher
    plan starts now; a lower one already running keeps its own days.
    """
    rank = RANK[plan_code]
    ends = [s.ends_at for s in _live(user) if RANK[s.plan] >= rank]
    return max([timezone.now(), *ends])


def _push_lower(user: User, plan_code: str, start: datetime, end: datetime) -> None:
    """A higher plan runs over a lower one: the lower one's remaining days
    move to after it instead of elapsing underneath."""
    rank = RANK[plan_code]
    length = end - start
    for sub in _live(user):
        if RANK[sub.plan] >= rank or sub.ends_at <= start:
            continue
        sub.ends_at += length
        if sub.starts_at > start:
            sub.starts_at += length
        sub.save(update_fields=["starts_at", "ends_at"])


def sync_user_plan(user: User) -> None:
    """Write the plan in force now onto the user (what courses read)."""
    now = timezone.now()
    live = _live(user)
    current = [s for s in live if s.starts_at <= now]
    if not current:
        plan, expires = "free", None
    else:
        best = max(current, key=lambda s: RANK[s.plan])
        plan, expires = best.plan, best.ends_at
        # Follow back-to-back periods of the same plan to the real end.
        for sub in sorted((s for s in live if s.plan == plan), key=lambda s: s.starts_at):
            if sub.starts_at <= expires:
                expires = max(expires, sub.ends_at)
    if user.plan != plan or user.plan_expires_at != expires:
        user.plan = plan
        user.plan_expires_at = expires
        user.save(update_fields=["plan", "plan_expires_at"])


def sync_due_plans() -> int:
    """Plans that ended, or periods that began, since the last run."""
    now = timezone.now()
    ended = User.objects.exclude(plan="free").filter(plan_expires_at__lte=now)
    began = Subscription.objects.filter(
        revoked_at__isnull=True, starts_at__lte=now, ends_at__gt=now
    ).exclude(plan=F("user__plan"))
    due = set(ended.values_list("pk", flat=True)) | set(began.values_list("user_id", flat=True))
    for user in User.objects.filter(pk__in=due):
        sync_user_plan(user)
    return len(due)


# ── Fulfilment ────────────────────────────────────────────────────────


def fulfil(order: Order) -> bool:
    """Grant what a paid order buys, once. False if the order was cancelled."""
    with transaction.atomic():
        locked = Order.objects.select_for_update().select_related("user", "course").get(pk=order.pk)
        if locked.status == Order.Status.PAID:
            return True
        if locked.status != Order.Status.PENDING:
            return False
        locked.status = Order.Status.PAID
        locked.paid_at = timezone.now()
        locked.save(update_fields=["status", "paid_at"])
        user = locked.user
        if locked.kind == Order.Kind.PLAN:
            start = period_start(user, locked.plan)
            end = add_months(start, locked.months or 1)
            _push_lower(user, locked.plan, start, end)
            Subscription.objects.create(
                user=user, plan=locked.plan, order=locked, starts_at=start, ends_at=end
            )
            sync_user_plan(user)
        else:
            assert locked.course is not None
            courses.grant_purchase(user, locked.course)
    log.info("billing: order %s paid (%s)", locked.pk, locked.provider)
    return True


def revoke(order: Order) -> None:
    """The payment was refunded: access ends at once (owner decision 2026-11-10)."""
    with transaction.atomic():
        locked = Order.objects.select_for_update().select_related("user", "course").get(pk=order.pk)
        if locked.status != Order.Status.PAID:
            return
        locked.status = Order.Status.REFUNDED
        locked.cancelled_at = timezone.now()
        locked.save(update_fields=["status", "cancelled_at"])
        user = locked.user
        if locked.kind == Order.Kind.PLAN:
            Subscription.objects.filter(order=locked).update(revoked_at=timezone.now())
            sync_user_plan(user)
        else:
            assert locked.course is not None
            courses.revoke_purchase(user, locked.course)
    log.info("billing: order %s refunded (%s)", locked.pk, locked.provider)


# ── Reading ───────────────────────────────────────────────────────────


def features(plan: Plan, locale: str) -> list[str]:
    text = getattr(plan, f"features_{locale}", "") or plan.features_uz
    return [line.strip() for line in text.splitlines() if line.strip()]
