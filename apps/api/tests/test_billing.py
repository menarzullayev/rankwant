"""Paid plans, orders, Payme and Click (ADR-0057)."""

from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from billing import payme, services
from billing.models import Order, PaymeTransaction, Plan, PlanPrice, Subscription
from core.models import User
from courses.models import (
    Course,
    CourseTranslation,
    Enrollment,
    Lesson,
    LessonTranslation,
    Module,
    Section,
)

pytestmark = pytest.mark.django_db

PAYME_KEY = "test-payme-key"
CLICK_SECRET = "test-click-secret"


@pytest.fixture(autouse=True)
def merchants(settings):
    settings.PAYME_MERCHANT_ID = "m-test"
    settings.PAYME_KEY = PAYME_KEY
    settings.PAYME_CHECKOUT_URL = "https://test.paycom.uz"
    settings.CLICK_SERVICE_ID = "31"
    settings.CLICK_MERCHANT_ID = "46"
    settings.CLICK_SECRET_KEY = CLICK_SECRET
    settings.CLICK_MERCHANT_USER_ID = ""
    return settings


@pytest.fixture
def pro() -> Plan:
    plan = Plan.objects.get(code="pro")
    plan.is_on_sale = True
    plan.features_uz = "Barcha pullik kurslar\n\nPro nishoni"
    plan.save()
    PlanPrice.objects.create(plan=plan, months=1, amount_uzs=49_000)
    PlanPrice.objects.create(plan=plan, months=12, amount_uzs=315_000, list_amount_uzs=525_000)
    return plan


def _client(user: User | None = None) -> APIClient:
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


def _paid_course(slug: str = "pullik", price: int = 97_000) -> tuple[Course, Lesson]:
    course = Course.objects.create(
        slug=slug, is_published=True, access=Course.Access.PAID, price_uzs=price
    )
    CourseTranslation.objects.create(course=course, locale="uz", title="Pullik kurs")
    module = Module.objects.create(course=course, order=1)
    section = Section.objects.create(module=module, order=1)
    lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
    LessonTranslation.objects.create(lesson=lesson, locale="uz", title="Dars", body="x")
    return course, lesson


def _order(user: User, provider: str = "payme", **kw) -> Order:
    kw.setdefault("kind", Order.Kind.PLAN)
    if kw["kind"] == Order.Kind.PLAN:
        kw.setdefault("plan", "pro")
        kw.setdefault("months", 1)
    kw.setdefault("amount_uzs", 49_000)
    return Order.objects.create(user=user, provider=provider, **kw)


# ── Payme ─────────────────────────────────────────────────────────────


def _rpc(method: str, params: dict, key: str = PAYME_KEY, rid: int = 1) -> dict:
    token = base64.b64encode(f"Paycom:{key}".encode()).decode()
    resp = APIClient().post(
        reverse("billing-payme"),
        {"jsonrpc": "2.0", "id": rid, "method": method, "params": params},
        format="json",
        HTTP_AUTHORIZATION=f"Basic {token}",
    )
    assert resp.status_code == 200
    body: dict = resp.json()
    return body


def _code(body: dict) -> int | None:
    code: int | None = body.get("error", {}).get("code")
    return code


class TestPayme:
    def test_wrong_key_is_refused(self, user):
        order = _order(user)
        body = _rpc(
            "CheckPerformTransaction",
            {"amount": 4_900_000, "account": {"order_id": order.pk}},
            key="nope",
        )
        assert _code(body) == -32504

    def test_checks_amount_and_order(self, user):
        order = _order(user)
        account = {"order_id": order.pk}
        assert _code(_rpc("CheckPerformTransaction", {"amount": 100, "account": account})) == -31001
        assert (
            _code(
                _rpc("CheckPerformTransaction", {"amount": 4_900_000, "account": {"order_id": 999}})
            )
            == -31050
        )
        ok = _rpc("CheckPerformTransaction", {"amount": 4_900_000, "account": account})
        assert ok["result"] == {"allow": True}

    def test_error_messages_are_localised(self, user):
        body = _rpc("CheckPerformTransaction", {"amount": 1, "account": {"order_id": 999}})
        assert set(body["error"]["message"]) == {"uz", "ru", "en"}
        assert body["error"]["data"] == "order_id"

    def test_scenario_create_and_cancel(self, user):
        order = _order(user)
        params = {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": order.pk}}
        first = _rpc("CreateTransaction", params)["result"]
        assert first["state"] == 1
        assert _rpc("CreateTransaction", params)["result"] == first
        other = {**params, "id": "tx2"}
        assert _code(_rpc("CreateTransaction", other)) == -31008
        checked = _rpc("CheckTransaction", {"id": "tx1"})["result"]
        assert (checked["state"], checked["reason"]) == (1, None)
        cancelled = _rpc("CancelTransaction", {"id": "tx1", "reason": 3})["result"]
        assert cancelled["state"] == -1
        assert _rpc("CancelTransaction", {"id": "tx1", "reason": 3})["result"] == cancelled
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_scenario_perform_then_refund(self, user, pro):
        order = _order(user)
        params = {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": order.pk}}
        _rpc("CreateTransaction", params)
        performed = _rpc("PerformTransaction", {"id": "tx1"})["result"]
        assert performed["state"] == 2
        assert _rpc("PerformTransaction", {"id": "tx1"})["result"] == performed
        user.refresh_from_db()
        assert user.plan == "pro"
        assert Subscription.objects.get().order == order
        refunded = _rpc("CancelTransaction", {"id": "tx1", "reason": 5})["result"]
        assert refunded["state"] == -2
        user.refresh_from_db()
        order.refresh_from_db()
        assert (user.plan, order.status) == ("free", Order.Status.REFUNDED)

    def test_a_paid_order_cannot_take_another_payment(self, user):
        order = _order(user)
        _rpc(
            "CreateTransaction",
            {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": order.pk}},
        )
        _rpc("PerformTransaction", {"id": "tx1"})
        again = _rpc(
            "CheckPerformTransaction", {"amount": 4_900_000, "account": {"order_id": order.pk}}
        )
        assert _code(again) == -31051

    def test_timeout_after_twelve_hours(self, user):
        order = _order(user)
        _rpc(
            "CreateTransaction",
            {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": order.pk}},
        )
        PaymeTransaction.objects.update(create_time=payme.now_ms() - payme.TIMEOUT_MS - 1)
        assert _code(_rpc("PerformTransaction", {"id": "tx1"})) == -31008
        tx = PaymeTransaction.objects.get()
        assert (tx.state, tx.reason) == (-1, 4)

    def test_a_repeated_create_past_the_timeout_is_refused_and_kept_expired(self, user):
        order = _order(user)
        params = {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": order.pk}}
        _rpc("CreateTransaction", params)
        PaymeTransaction.objects.update(create_time=payme.now_ms() - payme.TIMEOUT_MS - 1)
        assert _code(_rpc("CreateTransaction", params)) == -31008
        tx = PaymeTransaction.objects.get()
        order.refresh_from_db()
        assert (tx.state, tx.reason, order.status) == (-1, 4, Order.Status.CANCELLED)

    def test_the_hourly_task_expires_old_transactions_and_orders(self, user):
        from billing.tasks import expire_orders

        waiting = _order(user)
        _rpc(
            "CreateTransaction",
            {"id": "tx1", "time": 1, "amount": 4_900_000, "account": {"order_id": waiting.pk}},
        )
        PaymeTransaction.objects.update(create_time=payme.now_ms() - payme.TIMEOUT_MS - 1)
        forgotten = _order(user, "click")
        Order.objects.filter(pk=forgotten.pk).update(created_at=timezone.now() - timedelta(days=2))
        fresh = _order(user, "click")
        expire_orders()
        statuses = dict(Order.objects.values_list("pk", "status"))
        assert statuses[waiting.pk] == statuses[forgotten.pk] == Order.Status.CANCELLED
        assert statuses[fresh.pk] == Order.Status.PENDING

    def test_unknown_transaction_and_method(self, user):
        assert _code(_rpc("PerformTransaction", {"id": "none"})) == -31003
        assert _code(_rpc("Nope", {})) == -32601

    def test_statement(self, user):
        order = _order(user)
        _rpc(
            "CreateTransaction",
            {"id": "tx1", "time": 7, "amount": 4_900_000, "account": {"order_id": order.pk}},
        )
        rows = _rpc("GetStatement", {"from": 0, "to": payme.now_ms() + 1000})["result"][
            "transactions"
        ]
        assert [(r["id"], r["time"], r["account"]) for r in rows] == [
            ("tx1", 7, {"order_id": str(order.pk)})
        ]

    def test_bad_json_is_still_http_200(self):
        token = base64.b64encode(f"Paycom:{PAYME_KEY}".encode()).decode()
        resp = APIClient().post(
            reverse("billing-payme"),
            "{bad",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Basic {token}",
        )
        assert resp.status_code == 200
        assert resp.json()["error"]["code"] == -32700


# ── Click ─────────────────────────────────────────────────────────────


def _click(
    order: Order,
    action: int,
    *,
    trans: int = 777,
    prepare_id: int | None = None,
    amount: str | None = None,
    error: int = 0,
    secret: str = CLICK_SECRET,
) -> dict:
    data = {
        "click_trans_id": str(trans),
        "service_id": "31",
        "click_paydoc_id": "555",
        "merchant_trans_id": str(order.pk),
        "amount": amount or f"{order.amount_uzs}.00",
        "action": str(action),
        "error": str(error),
        "error_note": "",
        "sign_time": "2026-11-10 12:00:00",
    }
    if prepare_id is not None:
        data["merchant_prepare_id"] = str(prepare_id)
    parts = [data["click_trans_id"], data["service_id"], secret, data["merchant_trans_id"]]
    if prepare_id is not None:
        parts.append(data["merchant_prepare_id"])
    parts += [data["amount"], data["action"], data["sign_time"]]
    data["sign_string"] = hashlib.md5("".join(parts).encode()).hexdigest()
    resp = APIClient().post(reverse("billing-click"), data)
    assert resp.status_code == 200
    answer: dict = resp.json()
    return answer


class TestClick:
    def test_prepare_then_complete_opens_the_course(self, user):
        course, _ = _paid_course()
        order = _order(user, "click", kind=Order.Kind.COURSE, course=course, amount_uzs=97_000)
        prepared = _click(order, 0)
        assert prepared["error"] == 0
        done = _click(order, 1, prepare_id=prepared["merchant_prepare_id"])
        assert done["error"] == 0
        assert Enrollment.objects.get(user=user, course=course).source == Enrollment.Source.PURCHASE
        assert _click(order, 1, prepare_id=prepared["merchant_prepare_id"])["error"] == -4

    def test_refusals(self, user):
        order = _order(user, "click")
        assert _click(order, 0, secret="wrong")["error"] == -1
        assert _click(order, 0, amount="1.00")["error"] == -2
        assert _click(order, 3)["error"] == -3
        assert _click(order, 1, prepare_id=999)["error"] == -6
        missing = Order(pk=999_999, amount_uzs=49_000)
        assert _click(missing, 0)["error"] == -5

    def test_a_failed_charge_cancels_the_order(self, user):
        order = _order(user, "click")
        prepared = _click(order, 0)
        failed = _click(order, 1, prepare_id=prepared["merchant_prepare_id"], error=-5017)
        assert failed["error"] == -9
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED
        assert _click(order, 0, trans=778)["error"] == -9


# ── Orders API ────────────────────────────────────────────────────────


class TestOrders:
    def _create(self, user, **body):
        return _client(user).post(reverse("billing-order-list"), body, format="json")

    def test_plan_order_gives_a_payme_link(self, user, pro):
        resp = self._create(user, kind="plan", plan="pro", months=12, provider="payme")
        assert resp.status_code == 201
        body = resp.json()
        assert (body["amount_uzs"], body["status"]) == (315_000, "pending")
        encoded = body["pay_url"].rsplit("/", 1)[1]
        params = base64.b64decode(encoded).decode()
        assert f"ac.order_id={body['id']};a=31500000" in params
        assert params.startswith("m=m-test;")

    def test_click_link(self, user, pro):
        body = self._create(user, kind="plan", plan="pro", months=1, provider="click").json()
        assert body["pay_url"].startswith("https://my.click.uz/services/pay/?")
        assert "amount=49000.00" in body["pay_url"]
        assert f"transaction_param={body['id']}" in body["pay_url"]

    def test_not_on_sale_and_no_provider(self, user, pro, settings):
        assert (
            self._create(user, kind="plan", plan="plus", months=1, provider="payme").status_code
            == 400
        )
        assert (
            self._create(user, kind="plan", plan="pro", months=6, provider="payme").status_code
            == 400
        )
        settings.PAYME_KEY = ""
        resp = self._create(user, kind="plan", plan="pro", months=1, provider="payme")
        assert resp.status_code == 503
        assert resp.json()["error"]["code"] == "billing_provider_unavailable"

    def test_course_order_and_owned_course(self, user):
        course, _ = _paid_course()
        assert (
            self._create(user, kind="course", course=course.slug, provider="click").status_code
            == 201
        )
        Enrollment.objects.create(user=user, course=course, source=Enrollment.Source.PURCHASE)
        resp = self._create(user, kind="course", course=course.slug, provider="click")
        assert resp.status_code == 409

    def test_only_own_orders_and_cancel(self, user, other_user, pro):
        mine = _order(user)
        _order(other_user)
        rows = _client(user).get(reverse("billing-order-list")).json()
        assert [r["id"] for r in rows] == [mine.pk]
        assert (
            _client(other_user).get(reverse("billing-order-detail", args=[mine.pk])).status_code
            == 404
        )
        cancelled = _client(user).post(reverse("billing-order-cancel", args=[mine.pk])).json()
        assert (cancelled["status"], cancelled["pay_url"]) == ("cancelled", None)

    def test_overview(self, user, pro):
        guest = _client().get(reverse("billing-plans")).json()
        assert guest["plan"] == "free"
        assert set(guest["providers"]) == {"click", "payme"}
        offer = next(p for p in guest["plans"] if p["code"] == "pro")
        assert offer["features"] == ["Barcha pullik kurslar", "Pro nishoni"]
        assert [p["months"] for p in offer["prices"]] == [1, 12]
        services.fulfil(_order(user))
        mine = _client(user).get(reverse("billing-plans")).json()
        assert mine["plan"] == "pro"
        assert len(mine["periods"]) == 1


# ── Periods ───────────────────────────────────────────────────────────


class TestPeriods:
    def test_calendar_months(self):
        start = datetime(2026, 1, 31, 10, tzinfo=UTC)
        assert services.add_months(start, 1) == datetime(2026, 2, 28, 10, tzinfo=UTC)
        assert services.add_months(start, 12) == datetime(2027, 1, 31, 10, tzinfo=UTC)

    def test_same_plan_stacks(self, user):
        services.fulfil(_order(user))
        services.fulfil(_order(user))
        first, second = Subscription.objects.order_by("starts_at")
        assert second.starts_at == first.ends_at
        user.refresh_from_db()
        assert user.plan_expires_at == second.ends_at

    def test_a_lower_plan_waits_and_a_higher_starts_now(self, user):
        services.fulfil(_order(user, plan="pro"))
        services.fulfil(_order(user, plan="plus"))
        services.fulfil(_order(user, plan="judge"))
        pro_sub = Subscription.objects.get(plan="pro")
        assert Subscription.objects.get(plan="plus").starts_at == pro_sub.ends_at
        judge = Subscription.objects.get(plan="judge")
        assert judge.starts_at < pro_sub.ends_at
        user.refresh_from_db()
        assert user.plan == "judge"

    def test_sync_after_the_end(self, user):
        services.fulfil(_order(user))
        ended = timezone.now() - timedelta(days=1)
        Subscription.objects.update(starts_at=ended - timedelta(days=30), ends_at=ended)
        User.objects.filter(pk=user.pk).update(plan_expires_at=ended)
        assert services.sync_due_plans() == 1
        user.refresh_from_db()
        assert (user.plan, user.plan_expires_at) == ("free", None)

    def test_fulfil_is_once(self, user):
        order = _order(user)
        assert services.fulfil(order) and services.fulfil(order)
        assert Subscription.objects.count() == 1


# ── Courses and plans ─────────────────────────────────────────────────


class TestCourseAccess:
    def test_pro_opens_paid_courses_until_it_lapses(self, user):
        course, lesson = _paid_course()
        url = reverse("course-enroll", args=[course.slug])
        assert _client(user).post(url, {}).status_code == 402
        services.fulfil(_order(user))
        user.refresh_from_db()  # a real request reads the user afresh
        assert _client(user).post(url, {}).status_code == 201
        assert Enrollment.objects.get().source == Enrollment.Source.PLAN
        lesson_url = reverse("course-lesson", args=[course.slug, lesson.pk])
        assert _client(user).get(lesson_url).status_code == 200
        detail = _client(user).get(reverse("course-detail", args=[course.slug])).json()
        assert detail["plan_covers"] is True
        User.objects.filter(pk=user.pk).update(
            plan_expires_at=timezone.now() - timedelta(seconds=1)
        )
        user.refresh_from_db()
        assert _client(user).get(lesson_url).status_code == 403
        assert _client(user).post(url, {}).status_code == 402

    def test_plus_does_not_open_courses(self, user):
        course, _ = _paid_course()
        services.fulfil(_order(user, plan="plus"))
        user.refresh_from_db()
        assert (
            _client(user).post(reverse("course-enroll", args=[course.slug]), {}).status_code == 402
        )

    def test_a_bought_course_outlives_the_plan_and_a_refund_closes_it(self, user):
        course, _ = _paid_course()
        bought = _order(user, kind=Order.Kind.COURSE, course=course, amount_uzs=97_000)
        services.fulfil(bought)
        assert Enrollment.objects.get().source == Enrollment.Source.PURCHASE
        services.revoke(bought)
        assert not Enrollment.objects.exists()

    def test_a_refund_while_on_pro_keeps_the_course_through_the_plan(self, user):
        course, _ = _paid_course()
        services.fulfil(_order(user))
        bought = _order(user, kind=Order.Kind.COURSE, course=course, amount_uzs=97_000)
        services.fulfil(bought)
        user.refresh_from_db()
        services.revoke(bought)
        assert Enrollment.objects.get().source == Enrollment.Source.PLAN
