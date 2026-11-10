"""Click SHOP-API: Prepare (action 0) and Complete (action 1) (ADR-0057).

Read from docs.click.uz on 2026-11-10: Click posts form-encoded fields and
expects JSON back; the request is signed with
md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id
    [+ merchant_prepare_id] + amount + action + sign_time),
amounts are som with decimals, `merchant_trans_id` is our `Order.pk`, and a
negative `error` from Click on Complete means the charge failed: the
merchant cancels and answers -9.
"""

from __future__ import annotations

import hashlib
import hmac
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from billing import services
from billing.models import ClickTransaction, Order

NOTES = {
    0: "Success",
    -1: "SIGN CHECK FAILED!",
    -2: "Incorrect parameter amount",
    -3: "Action not found",
    -4: "Already paid",
    -5: "User does not exist",
    -6: "Transaction does not exist",
    -7: "Failed to update user",
    -8: "Error in request from click",
    -9: "Transaction cancelled",
}

PREPARE_FIELDS = (
    "click_trans_id",
    "service_id",
    "click_paydoc_id",
    "merchant_trans_id",
    "amount",
    "action",
    "error",
    "sign_time",
    "sign_string",
)


def _answer(code: int, **extra: Any) -> dict[str, Any]:
    return {**extra, "error": code, "error_note": NOTES[code]}


def sign(data: dict[str, str], *, with_prepare: bool) -> str:
    parts = [
        data["click_trans_id"],
        data["service_id"],
        settings.CLICK_SECRET_KEY,
        data["merchant_trans_id"],
    ]
    if with_prepare:
        parts.append(data["merchant_prepare_id"])
    parts += [data["amount"], data["action"], data["sign_time"]]
    return hashlib.md5("".join(parts).encode()).hexdigest()


def handle(data: dict[str, str]) -> dict[str, Any]:
    """One Prepare or Complete call; always an answer, never an exception."""
    if not settings.CLICK_SECRET_KEY or any(name not in data for name in PREPARE_FIELDS):
        return _answer(-8)
    action = data["action"]
    if action not in ("0", "1"):
        return _answer(-3)
    complete = action == "1"
    if complete and "merchant_prepare_id" not in data:
        return _answer(-8)
    if not hmac.compare_digest(sign(data, with_prepare=complete), data["sign_string"]):
        return _answer(-1)
    if data["service_id"] != str(settings.CLICK_SERVICE_ID):
        return _answer(-8)
    try:
        order_id = int(data["merchant_trans_id"])
        amount = Decimal(data["amount"])
        click_trans_id = int(data["click_trans_id"])
        click_error = int(data["error"])
    except (ValueError, InvalidOperation):
        return _answer(-8)
    ids = {"click_trans_id": click_trans_id, "merchant_trans_id": data["merchant_trans_id"]}
    order = Order.objects.filter(pk=order_id, provider=Order.Provider.CLICK).first()
    if order is None:
        return _answer(-5, **ids)
    if amount != Decimal(order.amount_uzs):
        return _answer(-2, **ids)
    if complete:
        return _complete(data, order, click_trans_id, click_error, ids)
    return _prepare(data, order, click_trans_id, amount, ids)


def _prepare(
    data: dict[str, str], order: Order, click_trans_id: int, amount: Decimal, ids: dict[str, Any]
) -> dict[str, Any]:
    if order.status == Order.Status.PAID:
        return _answer(-4, **ids)
    if order.status != Order.Status.PENDING:
        return _answer(-9, **ids)
    try:
        paydoc = int(data["click_paydoc_id"])
    except ValueError:
        return _answer(-8, **ids)
    tx, _ = ClickTransaction.objects.get_or_create(
        click_trans_id=click_trans_id,
        defaults={"click_paydoc_id": paydoc, "order": order, "amount": amount},
    )
    if tx.order_id != order.pk:
        return _answer(-8, **ids)
    return _answer(0, merchant_prepare_id=tx.pk, **ids)


def _complete(
    data: dict[str, str],
    order: Order,
    click_trans_id: int,
    click_error: int,
    ids: dict[str, Any],
) -> dict[str, Any]:
    with transaction.atomic():
        tx = (
            ClickTransaction.objects.select_for_update()
            .filter(pk=_int(data["merchant_prepare_id"]), click_trans_id=click_trans_id)
            .first()
        )
        if tx is None or tx.order_id != order.pk:
            return _answer(-6, **ids)
        if tx.status == ClickTransaction.Status.CONFIRMED:
            return _answer(-4, **ids)
        if tx.status == ClickTransaction.Status.CANCELLED:
            return _answer(-9, **ids)
        if click_error < 0:
            # Click could not charge the card: the order is void.
            tx.status = ClickTransaction.Status.CANCELLED
            tx.save(update_fields=["status"])
            services.cancel_pending(order)
            return _answer(-9, **ids)
        if not services.fulfil(order):
            tx.status = ClickTransaction.Status.CANCELLED
            tx.save(update_fields=["status"])
            return _answer(-9, **ids)
        tx.status = ClickTransaction.Status.CONFIRMED
        tx.confirmed_at = timezone.now()
        tx.save(update_fields=["status", "confirmed_at"])
    return _answer(0, merchant_confirm_id=tx.pk, **ids)


def _int(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        return 0
