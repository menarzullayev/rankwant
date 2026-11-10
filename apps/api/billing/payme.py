"""Payme Merchant API: Payme calls us over JSON-RPC 2.0 (ADR-0057).

Read from developer.help.paycom.uz on 2026-11-10: amounts in tiyin, times
in milliseconds, states 1 / 2 / -1 / -2, a created transaction times out
after 12 hours, and every Create / Perform / Cancel may arrive twice and
must then answer exactly as the first time. The account field is
`order_id` (our `Order.pk`).
"""

from __future__ import annotations

import base64
import binascii
import hmac
import logging
import time
from typing import Any

from django.conf import settings
from django.db import transaction

from billing import services
from billing.models import Order, PaymeTransaction

log = logging.getLogger(__name__)

TIMEOUT_MS = 43_200_000
REASON_TIMEOUT = 4

State = PaymeTransaction.State


class PaymeError(Exception):
    def __init__(self, code: int, message: dict[str, str], data: Any = None) -> None:
        super().__init__(code)
        self.code, self.message, self.data = code, message, data


def _msg(uz: str, ru: str, en: str) -> dict[str, str]:
    return {"uz": uz, "ru": ru, "en": en}


AUTH = _msg("Ruxsat yo'q", "Недостаточно привилегий", "Insufficient privileges")
BAD_AMOUNT = _msg("Noto'g'ri summa", "Неверная сумма", "Incorrect amount")
NO_ORDER = _msg("Buyurtma topilmadi", "Заказ не найден", "Order not found")
NOT_PAYABLE = _msg(
    "Buyurtmani to'lab bo'lmaydi", "Заказ нельзя оплатить", "The order cannot be paid"
)
BUSY = _msg(
    "Buyurtma boshqa to'lovni kutmoqda",
    "Заказ ожидает другой оплаты",
    "The order is awaiting another payment",
)
NO_TX = _msg("Tranzaksiya topilmadi", "Транзакция не найдена", "Transaction not found")
CANNOT = _msg(
    "Amalni bajarib bo'lmaydi",
    "Невозможно выполнить операцию",
    "Unable to perform the operation",
)
BAD_REQUEST = _msg("Noto'g'ri so'rov", "Неверный запрос", "Invalid request")
NO_METHOD = _msg("Metod topilmadi", "Метод не найден", "Method not found")
SYSTEM = _msg("Tizim xatosi", "Системная ошибка", "System error")


def now_ms() -> int:
    return int(time.time() * 1000)


def authorised(header: str) -> bool:
    """`Authorization: Basic base64(login:key)`; the key is the secret."""
    key = settings.PAYME_KEY
    if not key or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:], validate=True).decode()
    except (binascii.Error, UnicodeDecodeError):
        return False
    _, _, password = decoded.partition(":")
    return hmac.compare_digest(password.encode(), key.encode())


def _need(params: dict[str, Any], *names: str) -> None:
    if any(name not in params for name in names):
        raise PaymeError(-32600, BAD_REQUEST)


def _order(account: Any, *, lock: bool = False) -> Order:
    raw = account.get("order_id") if isinstance(account, dict) else None
    try:
        order_id = int(str(raw))
    except (TypeError, ValueError):
        raise PaymeError(-31050, NO_ORDER, "order_id") from None
    rows = Order.objects.select_for_update() if lock else Order.objects
    order = rows.filter(pk=order_id, provider=Order.Provider.PAYME).first()
    if order is None:
        raise PaymeError(-31050, NO_ORDER, "order_id")
    if order.status != Order.Status.PENDING:
        raise PaymeError(-31051, NOT_PAYABLE, "order_id")
    return order


def _check_amount(order: Order, amount: Any) -> None:
    if not isinstance(amount, int) or amount != order.amount_uzs * 100:
        raise PaymeError(-31001, BAD_AMOUNT)


def _tx(params: dict[str, Any], *, lock: bool = False) -> PaymeTransaction:
    _need(params, "id")
    rows = PaymeTransaction.objects.select_for_update() if lock else PaymeTransaction.objects
    tx = rows.filter(payme_id=str(params["id"])).select_related("order").first()
    if tx is None:
        raise PaymeError(-31003, NO_TX)
    return tx


def _expire(tx: PaymeTransaction) -> None:
    tx.state = State.CANCELLED
    tx.cancel_time = now_ms()
    tx.reason = REASON_TIMEOUT
    tx.save(update_fields=["state", "cancel_time", "reason"])
    services.cancel_pending(tx.order)


def check_perform(params: dict[str, Any]) -> dict[str, Any]:
    _need(params, "amount", "account")
    order = _order(params["account"])
    _check_amount(order, params["amount"])
    return {"allow": True}


def _find(payme_id: Any) -> PaymeTransaction | None:
    return PaymeTransaction.objects.select_for_update().filter(payme_id=str(payme_id)).first()


def create(params: dict[str, Any]) -> dict[str, Any]:
    _need(params, "id", "time", "amount", "account")
    # A repeat of a transaction past its 12 hours: expire it in its own
    # commit, then refuse (raising inside the block would roll it back).
    with transaction.atomic():
        old = _find(params["id"])
        expired = (
            old is not None
            and old.state == State.CREATED
            and now_ms() - old.create_time > TIMEOUT_MS
        )
        if expired and old is not None:
            _expire(old)
    if expired:
        raise PaymeError(-31008, CANNOT)
    with transaction.atomic():
        tx = _find(params["id"])
        if tx is not None:
            if tx.state != State.CREATED:
                raise PaymeError(-31008, CANNOT)
            return _created(tx)
        order = _order(params["account"], lock=True)
        # A repeat that raced the first call waited on the order lock: answer
        # it as the first one, not as a second transaction.
        raced = _find(params["id"])
        if raced is not None:
            if raced.state != State.CREATED:
                raise PaymeError(-31008, CANNOT)
            return _created(raced)
        _check_amount(order, params["amount"])
        if order.payme_transactions.filter(state__in=[State.CREATED, State.PERFORMED]).exists():
            # The sandbox expects -31008 here: a one-time account already
            # has a transaction waiting for payment.
            raise PaymeError(-31008, BUSY, "order_id")
        tx = PaymeTransaction.objects.create(
            payme_id=str(params["id"]),
            order=order,
            amount=params["amount"],
            time=int(params["time"]),
            create_time=now_ms(),
        )
    return _created(tx)


def _created(tx: PaymeTransaction) -> dict[str, Any]:
    return {"create_time": tx.create_time, "transaction": str(tx.pk), "state": tx.state}


def perform(params: dict[str, Any]) -> dict[str, Any]:
    with transaction.atomic():
        tx = _tx(params, lock=True)
        expired = tx.state == State.CREATED and now_ms() - tx.create_time > TIMEOUT_MS
        if expired:
            _expire(tx)  # committed below, then refused
        elif tx.state == State.CREATED:
            if not services.fulfil(tx.order):
                raise PaymeError(-31008, CANNOT)
            tx.state = State.PERFORMED
            tx.perform_time = now_ms()
            tx.save(update_fields=["state", "perform_time"])
        elif tx.state != State.PERFORMED:
            raise PaymeError(-31008, CANNOT)
    if expired:
        raise PaymeError(-31008, CANNOT)
    return {"transaction": str(tx.pk), "perform_time": tx.perform_time, "state": tx.state}


def cancel(params: dict[str, Any]) -> dict[str, Any]:
    _need(params, "id", "reason")
    with transaction.atomic():
        tx = _tx(params, lock=True)
        if tx.state == State.CREATED:
            tx.state = State.CANCELLED
            services.cancel_pending(tx.order)
        elif tx.state == State.PERFORMED:
            # A refund: what the order bought closes at once.
            services.revoke(tx.order)
            tx.state = State.CANCELLED_AFTER_PERFORM
        else:
            return _cancelled(tx)
        tx.cancel_time = now_ms()
        tx.reason = int(params["reason"])
        tx.save(update_fields=["state", "cancel_time", "reason"])
    return _cancelled(tx)


def _cancelled(tx: PaymeTransaction) -> dict[str, Any]:
    return {"transaction": str(tx.pk), "cancel_time": tx.cancel_time, "state": tx.state}


def check(params: dict[str, Any]) -> dict[str, Any]:
    tx = _tx(params)
    return {
        "create_time": tx.create_time,
        "perform_time": tx.perform_time,
        "cancel_time": tx.cancel_time,
        "transaction": str(tx.pk),
        "state": tx.state,
        "reason": tx.reason,
    }


def statement(params: dict[str, Any]) -> dict[str, Any]:
    _need(params, "from", "to")
    rows = PaymeTransaction.objects.filter(
        create_time__gte=int(params["from"]), create_time__lte=int(params["to"])
    ).order_by("create_time")
    return {
        "transactions": [
            {
                "id": tx.payme_id,
                "time": tx.time,
                "amount": tx.amount,
                "account": {"order_id": str(tx.order_id)},
                "create_time": tx.create_time,
                "perform_time": tx.perform_time,
                "cancel_time": tx.cancel_time,
                "transaction": str(tx.pk),
                "state": tx.state,
                "reason": tx.reason,
                "receivers": None,
            }
            for tx in rows
        ]
    }


METHODS = {
    "CheckPerformTransaction": check_perform,
    "CreateTransaction": create,
    "PerformTransaction": perform,
    "CancelTransaction": cancel,
    "CheckTransaction": check,
    "GetStatement": statement,
}


def handle(body: Any, auth_header: str) -> dict[str, Any]:
    """One JSON-RPC call; always an answer, never an exception (Payme needs 200)."""
    rpc_id = body.get("id") if isinstance(body, dict) else None
    try:
        if not authorised(auth_header):
            raise PaymeError(-32504, AUTH)
        if not isinstance(body, dict) or not isinstance(body.get("params"), dict):
            raise PaymeError(-32600, BAD_REQUEST)
        method = METHODS.get(str(body.get("method")))
        if method is None:
            raise PaymeError(-32601, NO_METHOD, body.get("method"))
        return {"jsonrpc": "2.0", "id": rpc_id, "result": method(body["params"])}
    except (TypeError, ValueError, KeyError):
        # A malformed field: still HTTP 200, as Payme requires.
        return _error(rpc_id, PaymeError(-32600, BAD_REQUEST))
    except PaymeError as error:
        return _error(rpc_id, error)
    except Exception:
        log.exception("payme: system error")
        return _error(rpc_id, PaymeError(-32400, SYSTEM))


def _error(rpc_id: Any, error: PaymeError) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "error": {"code": error.code, "message": error.message, "data": error.data},
    }
