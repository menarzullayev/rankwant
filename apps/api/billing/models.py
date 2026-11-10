"""Paid plans, orders and the two payment providers (ADR-0057).

A purchase is one prepaid period (1, 6 or 12 months) or one course, paid
once through Click or Payme; nothing renews by itself (owner decision
2026-11-10). An `Order` is the thing being paid for; the provider tables
keep each provider's own transaction record, because Payme and Click
disagree on everything from amount units to state codes.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from core.bases import CreatedModel


class PlanCode(models.TextChoices):
    PLUS = "plus", "Plus"
    PRO = "pro", "Pro"
    JUDGE = "judge", "Judge"


#: Higher rank includes everything below it.
RANK = {"free": 0, PlanCode.PLUS: 1, PlanCode.PRO: 2, PlanCode.JUDGE: 3}
#: Plans that open every paid course while they last (owner decision
#: 2026-11-10: Pro opens all paid courses; Judge includes Pro).
COVERS_COURSES = frozenset({PlanCode.PRO, PlanCode.JUDGE})
MONTHS = (1, 6, 12)


class Plan(models.Model):
    """A paid plan. What it offers beyond courses is staff-written text."""

    code = models.CharField(max_length=8, choices=PlanCode.choices, unique=True)
    is_on_sale = models.BooleanField(default=False)
    features_uz = models.TextField(blank=True, help_text="One feature per line.")
    features_ru = models.TextField(blank=True, help_text="One feature per line.")
    features_en = models.TextField(blank=True, help_text="One feature per line.")

    def __str__(self) -> str:
        return self.code


class PlanPrice(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="prices")
    months = models.PositiveSmallIntegerField(choices=[(m, str(m)) for m in MONTHS])
    #: What the buyer pays, in som.
    amount_uzs = models.PositiveIntegerField()
    #: The struck-through price shown next to it; 0 shows none.
    list_amount_uzs = models.PositiveIntegerField(default=0)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["plan", "months"], name="plan_price_once"),
            models.CheckConstraint(
                condition=models.Q(amount_uzs__gt=0), name="plan_price_positive"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.plan_id}:{self.months}"


class Order(CreatedModel):
    class Kind(models.TextChoices):
        PLAN = "plan", "Plan"
        COURSE = "course", "Course"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"

    #: A financial record outlives the account (accounts are anonymised,
    #: not deleted).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    kind = models.CharField(max_length=8, choices=Kind.choices)
    plan = models.CharField(max_length=8, choices=PlanCode.choices, blank=True)
    months = models.PositiveSmallIntegerField(null=True, blank=True)
    course = models.ForeignKey(
        "courses.Course", null=True, blank=True, on_delete=models.PROTECT, related_name="orders"
    )
    #: Frozen when the order is made: a later price change never touches it.
    amount_uzs = models.PositiveIntegerField()
    provider = models.CharField(max_length=8, choices=Provider.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at", "-id"]
        indexes: ClassVar = [models.Index(fields=["status", "created_at"])]

    def __str__(self) -> str:
        return f"#{self.pk} {self.kind} {self.status}"


class Subscription(CreatedModel):
    """One paid period of a plan. Periods of the same plan follow each other."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.CharField(max_length=8, choices=PlanCode.choices)
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="subscription")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    #: Set when the payment is refunded: the period ends at once.
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["starts_at", "id"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.plan} {self.starts_at:%Y-%m-%d}..{self.ends_at:%Y-%m-%d}"


class PaymeTransaction(models.Model):
    """Payme's transaction, in Payme's own units (tiyin, milliseconds)."""

    class State(models.IntegerChoices):
        CREATED = 1, "Created"
        PERFORMED = 2, "Performed"
        CANCELLED = -1, "Cancelled"
        CANCELLED_AFTER_PERFORM = -2, "Cancelled after perform"

    payme_id = models.CharField(max_length=32, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payme_transactions")
    amount = models.PositiveBigIntegerField()
    #: Payme's own creation time of the transaction.
    time = models.BigIntegerField()
    create_time = models.BigIntegerField()
    perform_time = models.BigIntegerField(default=0)
    cancel_time = models.BigIntegerField(default=0)
    state = models.SmallIntegerField(choices=State.choices, default=State.CREATED)
    reason = models.SmallIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"payme {self.payme_id} state={self.state}"


class ClickTransaction(CreatedModel):
    class Status(models.TextChoices):
        PREPARED = "prepared", "Prepared"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    click_trans_id = models.BigIntegerField(unique=True)
    click_paydoc_id = models.BigIntegerField()
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="click_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PREPARED)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"click {self.click_trans_id} {self.status}"
