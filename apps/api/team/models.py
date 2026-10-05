"""The team page (`/team`) — who builds the platform.

Three things are kept here, and the page draws them differently:

- `Department` and `Role` are the page's running joke: twelve departments
  and two dozen titles, every one of them held by the member marked
  `holds_all_roles`. They are data so that the owner can add a title
  without a deploy.
- `Member` is a real person: the founder, a teammate, or somebody who
  contributed. Members are what the page shows in its serious mode and in
  the contributors section.

Text is stored in Uzbek, Russian and English, the three languages the
page's content is written in; a blank translation falls back to Uzbek.
"""

from __future__ import annotations

from typing import ClassVar

from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q

from core.bases import TimeStampedModel


class Department(models.Model):
    name_uz = models.CharField(max_length=80)
    name_ru = models.CharField(max_length=80, blank=True)
    name_en = models.CharField(max_length=80, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "pk"]

    def __str__(self) -> str:
        return self.name_uz


class Role(TimeStampedModel):
    class Tone(models.TextChoices):
        OK = "ok", "Yaxshi"
        WARN = "warn", "Diqqat"

    # PROTECT: deleting a department must not silently take its roles along.
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="roles")
    title_uz = models.CharField(max_length=120)
    title_ru = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    about_uz = models.CharField(max_length=300)
    about_ru = models.CharField(max_length=300, blank=True)
    about_en = models.CharField(max_length=300, blank=True)
    reports_to_uz = models.CharField(max_length=120, blank=True)
    reports_to_ru = models.CharField(max_length=120, blank=True)
    reports_to_en = models.CharField(max_length=120, blank=True)
    status_uz = models.CharField(max_length=60, blank=True)
    status_ru = models.CharField(max_length=60, blank=True)
    status_en = models.CharField(max_length=60, blank=True)
    #: A short mark on the avatar (CEO, API, </>). Not translated.
    badge = models.CharField(max_length=8, blank=True)
    #: Hue of the ring around the photo, so copies of one face can be told apart.
    hue = models.PositiveSmallIntegerField(default=262, validators=[MaxValueValidator(359)])
    tone = models.CharField(max_length=8, choices=Tone.choices, default=Tone.OK)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar = ["department__order", "order", "pk"]

    def __str__(self) -> str:
        return self.title_uz


class Member(TimeStampedModel):
    class Section(models.TextChoices):
        CORE = "core", "Asosiy jamoa"
        CONTRIBUTOR = "contributor", "Hissa qo'shgan"

    section = models.CharField(max_length=16, choices=Section.choices, default=Section.CONTRIBUTOR)
    name = models.CharField(max_length=120)
    title_uz = models.CharField(max_length=120)
    title_ru = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    #: One line of who this is outside the project: where they study or work.
    context_uz = models.CharField(max_length=200, blank=True)
    context_ru = models.CharField(max_length=200, blank=True)
    context_en = models.CharField(max_length=200, blank=True)
    #: A URL or a site path (`/team/name.jpg`), not an upload: the page has a
    #: handful of people, and a second storage path for a handful of files is
    #: not worth its upkeep.
    photo_url = models.CharField(max_length=500, blank=True)
    telegram_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    #: The member every `Role` belongs to. At most one.
    holds_all_roles = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar = ["section", "order", "pk"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["holds_all_roles"],
                condition=Q(holds_all_roles=True),
                name="team_one_member_holds_all_roles",
            )
        ]

    def __str__(self) -> str:
        return self.name
