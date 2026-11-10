from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from billing import payme, services
from billing.models import ClickTransaction, Order, PaymeTransaction

#: An unpaid order is dropped after a day (a Payme transaction times out
#: after 12 hours on Payme's side; Click has no stated limit).
ORDER_TTL = timedelta(hours=24)


@shared_task(name="billing.sync_plans")
def sync_plans() -> int:
    """Plans that ended or periods that began: write them onto the user."""
    return services.sync_due_plans()


@shared_task(name="billing.expire_orders")
def expire_orders() -> int:
    """Close Payme transactions past their 12 hours and orders past a day."""
    cutoff_ms = payme.now_ms() - payme.TIMEOUT_MS
    for tx in PaymeTransaction.objects.filter(
        state=PaymeTransaction.State.CREATED, create_time__lt=cutoff_ms
    ).select_related("order"):
        payme._expire(tx)
    stale = (
        Order.objects.filter(status=Order.Status.PENDING, created_at__lt=timezone.now() - ORDER_TTL)
        .exclude(payme_transactions__state=PaymeTransaction.State.CREATED)
        .exclude(click_transactions__status=ClickTransaction.Status.CONFIRMED)
    )
    count = 0
    for order in stale:
        count += services.cancel_pending(order)
    return count
