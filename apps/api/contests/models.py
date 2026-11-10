"""Musobaqa — 05-domain-model 🔒."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.bases import CreatedModel, UpdatedModel
from core.mixins import TimeWindowMixin


class Contest(TimeWindowMixin, CreatedModel):
    class Scoring(models.TextChoices):
        ACM = "acm", "ACM/ICPC"
        IOI = "ioi", "IOI"

    slug = models.SlugField(unique=True, max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    freeze_minutes = models.PositiveIntegerField(
        default=0, help_text="Oxirgi N daqiqada standings muzlatiladi"
    )
    scoring_type = models.CharField(max_length=8, choices=Scoring.choices, default=Scoring.ACM)

    # Contests reytingi FAQAT shunga tayanadi (ADR-0006)
    is_rated = models.BooleanField(default=False)
    is_virtual = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    mirror_of = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="mirrors"
    )
    ratings_applied_at = models.DateTimeField(null=True, blank=True)
    #: Hakamlar — profilda «Hakam» nishoni (ADR-0018); admin paneldan.
    jury = models.ManyToManyField("core.User", blank=True, related_name="jury_contests")
    #: Organizatorlar (ADR-0025): o'z kontestini draft qilib yaratadi va
    #: tahrirlaydi (`is_public=False`); nashr — staff-ops. Bir foydalanuvchi
    #: bir vaqtda bir necha kontestga ega bo'lishi mumkin — shuning uchun M2M.
    organizers = models.ManyToManyField(
        "core.User",
        blank=True,
        related_name="organized_contests",
        help_text="O'z kontestini draft qilib yaratadi/tahrirlaydi; nashr — staff-ops (ADR-0025)",
    )
    #: Testers (ADR-0055, part 2): open the problems and send solutions
    #: before the start. Like every other insider they may take part, but
    #: unrated — see `contests.insiders`.
    testers = models.ManyToManyField(
        "core.User",
        blank=True,
        related_name="tested_contests",
        help_text="Boshlanishdan oldin masalalarni sinaydi; qatnashsa reytingsiz (ADR-0055)",
    )

    # ── Hacking (ADR-0020) ───────────────────────────────────────────
    #: `contest_room` siyosati: raund davomida xona ichida hack.
    #: Faqat IOI (ballli) musobaqada ma'noga ega — ACM tartibi yechilgan
    #: masala va jarimadan iborat, hack bali unga sig'maydi.
    hack_room = models.BooleanField(default=False)
    #: `open_phase` oynasi `end_at` dan keyin shuncha daqiqa ochiq turadi.
    #: 0 — ochiq faza yo'q. Reyting shu oyna yopilgunicha KUTADI
    #: (ADR-0020, 7-tamoyil).
    hack_open_minutes = models.PositiveIntegerField(default=0)
    #: `uphack` oynasi: reyting qo'llangach shuncha kun. 0 — o'chiq.
    uphack_days = models.PositiveSmallIntegerField(default=7)
    #: Oyna yopilgach: muvaffaqiyatli hack testlari to'plamga qo'shildi va
    #: `AC` lar qayta navbatga qo'yildi.
    hack_tests_added_at = models.DateTimeField(null=True, blank=True)
    #: Qayta tekshiruv ham tugadi — endi reyting qo'llansa bo'ladi.
    hack_phase_closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-start_at"]

    def __str__(self) -> str:
        return self.slug

    @property
    def freeze_at(self) -> datetime | None:
        """Muzlatish boshlanadigan payt — yo'q bo'lsa None."""
        if not self.freeze_minutes:
            return None
        return self.end_at - timedelta(minutes=self.freeze_minutes)

    @property
    def is_frozen(self) -> bool:
        """Oxirgi `freeze_minutes` — standings yangilanishi to'xtaydi."""
        frozen_from = self.freeze_at
        return bool(frozen_from and self.is_running and timezone.now() >= frozen_from)

    @property
    def hack_open_until(self) -> datetime | None:
        """Ochiq faza qachon yopiladi — o'chiq bo'lsa `None`."""
        if not self.hack_open_minutes:
            return None
        return self.end_at + timedelta(minutes=self.hack_open_minutes)

    @property
    def is_hack_open(self) -> bool:
        """Ochiq faza hozir ketyaptimi (musobaqa tugagan, oyna yopilmagan)."""
        until = self.hack_open_until
        return bool(until and self.is_finished and timezone.now() < until)

    @property
    def uphack_until(self) -> datetime | None:
        """Uphack oynasi qachon yopiladi. Reyting qo'llanmaguncha `None`."""
        if not self.uphack_days or self.ratings_applied_at is None:
            return None
        return self.ratings_applied_at + timedelta(days=self.uphack_days)


class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="problems")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.PROTECT, related_name="contest_entries"
    )
    index_letter = models.CharField(max_length=3)
    points = models.PositiveIntegerField(default=100)

    class Meta:
        ordering: ClassVar = ["index_letter"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "index_letter"], name="uniq_contest_index"),
            models.UniqueConstraint(fields=["contest", "problem"], name="uniq_contest_problem"),
        ]

    def __str__(self) -> str:
        return f"{self.contest.slug}/{self.index_letter}"


class ContestRegistration(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="contest_registrations"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    virtual_start_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "user"], name="uniq_contest_registration")
        ]

    def __str__(self) -> str:
        return f"{self.contest_id}/{self.user_id}"


class StandingQuerySet(models.QuerySet["Standing"]):
    def official(self) -> StandingQuerySet:
        """Rows that count: ratings, places, certificates, prizes.

        An insider's row (ADR-0055, part 2) is shown in the table with a
        star and no place; everything that ranks people reads this.
        """
        return self.filter(insider_role="")


class Standing(UpdatedModel):
    """MATERIALLASHTIRILGAN — live hisoblash 500 parallel submit ostida
    standings so'rovini buzadi (04-prd NFR)."""

    class InsiderRole(models.TextChoices):
        AUTHOR = "author", "Muallif"
        TESTER = "tester", "Sinovchi"
        JURY = "jury", "Hakam"
        ORGANIZER = "organizer", "Tashkilotchi"

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="standings")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="standings")
    #: Official place, 1..N among official rows. An insider's row has 0:
    #: it has no place, and a reader that forgot `official()` cannot
    #: mistake it for a winner.
    rank = models.PositiveIntegerField(default=0)
    #: Order in the full table, insiders included — what the public table
    #: sorts by.
    position = models.PositiveIntegerField(default=0)
    #: Set when the participant knew the problems beforehand: the row is
    #: unofficial (ADR-0055, part 2).
    insider_role = models.CharField(max_length=12, choices=InsiderRole.choices, blank=True)
    solved_count = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    last_ac_at = models.DateTimeField(null=True, blank=True)
    #: Hack bali (ADR-0020): `contest_room` da +100 / −50. Manfiy bo'lishi
    #: mumkin, shuning uchun `IntegerField`. Alohida ustun — jadvalda
    #: ko'rsatiladi va `total_score` ga qo'shiladi.
    hack_score = models.IntegerField(default=0)
    hacks_successful = models.PositiveSmallIntegerField(default=0)
    hacks_unsuccessful = models.PositiveSmallIntegerField(default=0)

    objects = StandingQuerySet.as_manager()

    class Meta:
        ordering: ClassVar = ["position"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "user"], name="uniq_contest_standing")
        ]
        indexes: ClassVar = [
            models.Index(fields=["contest", "rank"], name="standing_board"),
            models.Index(fields=["contest", "position"], name="standing_table"),
        ]

    @property
    def is_official(self) -> bool:
        return not self.insider_role

    def __str__(self) -> str:
        return f"{self.contest.slug} #{self.rank} {self.user_id}"


class Certificate(models.Model):
    """Musobaqa sertifikati (ADR-0019).

    ID — tekshirish manzilidagi noyob kalit (QR shunga olib keladi). Ism
    berilgan paytdagi holatda saqlanadi: keyin taxallus yoki ism
    almashsa ham hujjat o'zgarmaydi.
    """

    class Tier(models.TextChoices):
        GOLD = "gold", "1-o'rin"
        SILVER = "silver", "2-o'rin"
        BRONZE = "bronze", "3-o'rin"
        TOP10 = "top10", "Eng yaxshi 10%"
        PARTICIPANT = "participant", "Ishtirokchi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="certificates")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=150)
    place = models.PositiveIntegerField()
    participants = models.PositiveIntegerField()
    tier = models.CharField(max_length=12, choices=Tier.choices)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-issued_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "contest"], name="uniq_certificate"),
        ]

    def __str__(self) -> str:
        return f"{self.contest_id}:{self.user_id} ({self.tier})"


class Clarification(CreatedModel):
    """A participant's question and the jury's answer — or a jury announcement
    (ADR-0055, part 3).

    A question is private: its author and the moderators see it. The answer
    goes to the author, or to everybody when the jury makes it public. An
    announcement is a public row with no question and no author. Once the
    contest is finalized every answered row is public; the author's name
    never is.
    """

    class QuickAnswer(models.TextChoices):
        # Drawn in the reader's language on the site, so stored as a code.
        YES = "yes", "Ha"
        NO = "no", "Yo'q"
        READ_STATEMENT = "read_statement", "Shartni o'qing"
        NO_COMMENT = "no_comment", "Izoh yo'q"

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="clarifications")
    #: `None` — about the contest as a whole.
    problem = models.ForeignKey(
        ContestProblem, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    #: `None` for a jury announcement.
    author = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="contest_questions",
    )
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    answer_code = models.CharField(max_length=16, choices=QuickAnswer.choices, blank=True)
    answered_by = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    answered_at = models.DateTimeField(null=True, blank=True)
    #: Shown to everybody: an announcement, or an answer the jury published.
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering: ClassVar = ["-created_at", "-pk"]
        indexes: ClassVar = [
            models.Index(fields=["contest", "-created_at"], name="clarification_feed"),
            models.Index(fields=["contest", "author"], name="clarification_author"),
        ]

    def __str__(self) -> str:
        return f"{self.contest_id}/{self.pk}"

    @property
    def is_answered(self) -> bool:
        return self.answered_at is not None
