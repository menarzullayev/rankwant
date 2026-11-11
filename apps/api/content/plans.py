"""Writing a study plan from outside the content app (ADR-0060 § 2.4).

An import (the Abramyan book) builds a plan with sections and steps; it
goes through here rather than reaching into `content.models`, so the app
boundary (`tools/check_architecture.py`) holds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.db import transaction

from content.models import Roadmap, RoadmapSection, RoadmapStep


@dataclass(frozen=True)
class Section:
    order: int
    title: str
    description: str = ""
    translations: dict[str, dict[str, str]] = field(default_factory=dict)
    #: The section's problems, in order.
    problems: tuple[Any, ...] = ()


@transaction.atomic
def upsert(
    *,
    slug: str,
    title: str,
    description: str,
    locale: str,
    translations: dict[str, dict[str, str]],
    sections: list[Section],
) -> Roadmap:
    """Create or update a sectioned plan; a step is its global order."""
    roadmap, _ = Roadmap.objects.update_or_create(
        slug=slug,
        defaults={
            "title": title,
            "description": description,
            "locale": locale,
            "translations": translations,
            "track": Roadmap.Track.GENERAL,
        },
    )
    order = 0
    for spec in sections:
        section, _ = RoadmapSection.objects.update_or_create(
            roadmap=roadmap,
            order=spec.order,
            defaults={
                "title": spec.title,
                "description": spec.description,
                "translations": spec.translations,
            },
        )
        for problem in spec.problems:
            order += 1
            RoadmapStep.objects.update_or_create(
                roadmap=roadmap,
                order=order,
                defaults={"problem": problem, "section": section, "title": ""},
            )
    return roadmap


def publish(slug: str) -> int:
    """Make the plan visible; returns the number of plans changed."""
    return Roadmap.objects.filter(slug=slug).update(is_published=True)
