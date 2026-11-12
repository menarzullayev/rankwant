"""The monthly budget (decision ⑧, ADR-0065 § 2.11).

Spend is what the replies would cost at API prices, as the provider reports
it. Today every reply goes through `claude -p` on the owner's subscription,
so the number is a measure, not a bill; the switch to `claude -p` when the
budget runs out (decision ⑨) applies once an API provider exists.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db.models import F, Sum

from tutor.limits import local_day
from tutor.models import Budget, Spend

log = logging.getLogger(__name__)

#: Decision ⑧: warn at 80 % of the month's limit.
WARN_AT = 80


def month_start(day: date) -> date:
    return day.replace(day=1)


def limit_usd() -> Decimal:
    row = Budget.objects.order_by("pk").first()
    return row.month_limit_usd if row else Decimal("0")


def set_limit(value: Decimal) -> Decimal:
    row = Budget.objects.order_by("pk").first() or Budget()
    row.month_limit_usd = value
    row.save()
    return row.month_limit_usd


def spent_usd(day: date) -> Decimal:
    total = Spend.objects.filter(day__gte=month_start(day), day__lte=day).aggregate(
        s=Sum("cost_usd")
    )
    return total["s"] or Decimal("0")


def percent(spent: Decimal, limit: Decimal) -> float | None:
    return float(spent / limit * 100) if limit > 0 else None


def record(model: str, cost: Decimal, at: datetime | None = None) -> None:
    """Add one reply to the day's spend; log once when the month crosses 80 %."""
    day = local_day(at)
    limit = limit_usd()
    before = spent_usd(day)
    row, _ = Spend.objects.get_or_create(day=day, model=model[:64])
    Spend.objects.filter(pk=row.pk).update(replies=F("replies") + 1, cost_usd=F("cost_usd") + cost)
    was, now = percent(before, limit), percent(before + cost, limit)
    if was is not None and now is not None and was < WARN_AT <= now:
        log.warning("AI tutor budget at %.0f%% of %s USD this month", now, limit)


def summary(now: datetime | None = None) -> dict[str, Any]:
    day = local_day(now)
    rows = (
        Spend.objects.filter(day__gte=month_start(day), day__lte=day)
        .values("model")
        .annotate(replies=Sum("replies"), cost=Sum("cost_usd"))
        .order_by("-cost", "model")
    )
    spent = sum((r["cost"] or Decimal("0") for r in rows), Decimal("0"))
    limit = limit_usd()
    share = percent(spent, limit)
    return {
        "month": day.strftime("%Y-%m"),
        "spent_usd": spent,
        "replies": sum(r["replies"] or 0 for r in rows),
        "limit_usd": limit,
        "percent": share,
        "warning": share is not None and share >= WARN_AT,
        "over": share is not None and share >= 100,
        "by_model": [
            {
                "model": r["model"],
                "replies": r["replies"] or 0,
                "spent_usd": r["cost"] or Decimal("0"),
            }
            for r in rows
        ],
    }
