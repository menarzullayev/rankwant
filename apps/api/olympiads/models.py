"""The olympiad archive, imported from cp.uz (ADR-0062 § 2.6, stage 6).

Seasons and their routes (the paths to the IOI, EGOI, …), the events on them,
the problem statements of past rounds, and the published results with their
participants. Nothing here is judged: the statements carry no tests; their
links lead to the original and to where the problem can be solved.

Two parts are personal data or unlicensed text (owner, 2026-11-11):

- participants (name and country, from official results; most are pupils);
- the selection statements copied from KEP.uz.

They are imported from a cp.uz clone on the host, never kept in the
repository, and a removal request is honoured by `removed_at`: the row is
hidden and a later import leaves it hidden.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import TimeStampedModel


class Season(TimeStampedModel):
    slug = models.SlugField(unique=True, max_length=40)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    #: The season's routes as cp.uz draws them: code, title, description, kind.
    routes = models.JSONField(default=list, blank=True)
    order = models.IntegerField(default=0)
    #: The cp.uz commit this row came from.
    source_commit = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering: ClassVar = ["-start_date", "-order"]

    def __str__(self) -> str:
        return self.slug


class Event(TimeStampedModel):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="events")
    slug = models.SlugField(unique=True, max_length=80)
    code = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=300)
    short_title = models.CharField(max_length=120, blank=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    #: `international`, `national`, `selection`, … as cp.uz has it.
    kind = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, blank=True)
    verification = models.CharField(max_length=20, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    date_label = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=200, blank=True)
    mode = models.CharField(max_length=20, blank=True)
    platform = models.CharField(max_length=120, blank=True)
    organizer = models.CharField(max_length=300, blank=True)
    eligibility = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    #: Which season routes the event sits on: `[{route_code, order, label, …}]`.
    routes = models.JSONField(default=list, blank=True)
    #: Official pages, scoreboards, task archives: `[{type, title, url, …}]`.
    resources = models.JSONField(default=list, blank=True)
    source_commit = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering: ClassVar = ["start_date", "order", "slug"]

    def __str__(self) -> str:
        return self.slug


class ProblemSet(models.Model):
    """A day or round of an event."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sets")
    slug = models.SlugField(max_length=60)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "slug"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["event", "slug"], name="uniq_olympiad_set")
        ]

    def __str__(self) -> str:
        return f"{self.event_id}/{self.slug}"


class Task(models.Model):
    """A statement of a past round, in Uzbek; not a judged problem."""

    problem_set = models.ForeignKey(ProblemSet, on_delete=models.CASCADE, related_name="tasks")
    slug = models.SlugField(max_length=80)
    code = models.CharField(max_length=10, blank=True)
    title = models.CharField(max_length=300)
    original_title = models.CharField(max_length=300, blank=True)
    statement = models.TextField(blank=True, help_text="Markdown + LaTeX")
    translation_status = models.CharField(max_length=40, blank=True)
    problem_type = models.CharField(max_length=40, blank=True)
    time_limit_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_limit_mb = models.PositiveIntegerField(null=True, blank=True)
    max_score = models.PositiveIntegerField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    #: `[{kind: original | practice, title, url, platform, …}]`.
    links = models.JSONField(default=list, blank=True)
    statement_pdf = models.URLField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    #: Copied from KEP.uz: no licence and no partnership covers it, so the
    #: page says so and the statement is removed on request.
    from_kep = models.BooleanField(default=False)
    #: A takedown: hidden, and a later import leaves it hidden.
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["order", "code", "slug"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem_set", "slug"], name="uniq_olympiad_task")
        ]

    def __str__(self) -> str:
        return f"{self.problem_set_id}/{self.slug}"


class Participant(models.Model):
    """A name and a country from official results (personal data)."""

    slug = models.SlugField(unique=True, max_length=120)
    full_name = models.CharField(max_length=200)
    country_code = models.CharField(max_length=3, blank=True)
    #: A removal request: hidden with all results, and a later import keeps
    #: it hidden (the slug is remembered, the name is cleared).
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["full_name"]

    def __str__(self) -> str:
        return self.slug


class Result(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="results")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="results")
    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    medal = models.CharField(max_length=20, blank=True)
    #: An Uzbekistan participant (cp.uz marks them).
    is_local = models.BooleanField(default=True)
    result_url = models.URLField(max_length=500, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "rank"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["event", "participant"], name="uniq_olympiad_result")
        ]

    def __str__(self) -> str:
        return f"{self.event_id}:{self.participant_id}"
