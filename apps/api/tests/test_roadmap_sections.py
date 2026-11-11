"""Study plans with sections, translations and a page each (ADR-0060 § 2.4)."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from content.models import Roadmap, RoadmapSection, RoadmapStep
from core.models import User
from judging.models import Attempt
from judging.services import apply_result
from problems.models import Problem, ProblemTranslation

pytestmark = pytest.mark.django_db


@pytest.fixture
def plan(db) -> Roadmap:
    roadmap = Roadmap.objects.create(
        slug="abramyan",
        title="Abramyan: 1000 masala",
        description="Boshlang'ich dasturlash",
        locale="uz",
        translations={
            "ru": {"title": "Абрамян: 1000 задач"},
            "kaa": {"title": "Abramyan: 1000 másele"},
        },
        is_published=True,
    )
    begin = RoadmapSection.objects.create(
        roadmap=roadmap,
        order=1,
        title="Begin",
        description="Kiritish va chiqarish",
        translations={"ru": {"title": "Begin", "description": "Ввод и вывод"}},
    )
    integer = RoadmapSection.objects.create(roadmap=roadmap, order=2, title="Integer")
    for order, (slug, section) in enumerate(
        [("begin1", begin), ("begin2", begin), ("integer1", integer)], 1
    ):
        problem = Problem.objects.create(
            slug=slug,
            title=f"{slug.capitalize()}. Nom",
            statement="…",
            difficulty=800,
            is_public=True,
            is_official=False,
        )
        RoadmapStep.objects.create(roadmap=roadmap, order=order, problem=problem, section=section)
    ProblemTranslation.objects.create(
        problem=Problem.objects.get(slug="begin1"),
        locale="ru",
        title="Begin1. Название",
        statement="…",
    )
    return roadmap


def _solve(user: User, slug: str, language) -> None:  # type: ignore[no-untyped-def]
    attempt = Attempt.objects.create(
        user=user, problem=Problem.objects.get(slug=slug), language=language, source_code="x"
    )
    apply_result({"attempt_id": attempt.pk, "verdict": "AC"})


def test_the_plan_lists_its_sections_with_progress(plan, user, language) -> None:
    _solve(user, "begin1", language)
    client = APIClient()
    client.force_authenticate(user)
    body = client.get("/api/v1/roadmaps/abramyan/").json()
    assert body["section_count"] == 2 and body["step_count"] == 3
    assert [(s["order"], s["step_count"], s["solved_steps"]) for s in body["sections"]] == [
        (1, 2, 1),
        (2, 1, 0),
    ]
    # An unofficial solve counts for the plan (ADR-0060 § 2.3).
    assert body["solved_steps"] == 1
    # Steps are read a section at a time.
    assert body["steps"] == []


def test_a_section_page_has_its_steps_and_neighbours(plan, user, language) -> None:
    _solve(user, "begin2", language)
    client = APIClient()
    client.force_authenticate(user)
    first = client.get("/api/v1/roadmaps/abramyan/sections/1/").json()
    assert [(s["problem"], s["solved"]) for s in first["steps"]] == [
        ("begin1", False),
        ("begin2", True),
    ]
    assert (first["previous"], first["next"]) == (None, 2)
    second = client.get("/api/v1/roadmaps/abramyan/sections/2/").json()
    assert (second["previous"], second["next"]) == (1, None)
    assert client.get("/api/v1/roadmaps/abramyan/sections/9/").status_code == 404


def test_texts_follow_the_reader(plan) -> None:
    client = APIClient()
    ru = client.get("/api/v1/roadmaps/abramyan/?lang=ru").json()
    assert (ru["title"], ru["locale"]) == ("Абрамян: 1000 задач", "ru")
    # A translation without a description falls back to the base one.
    assert ru["description"] == "Boshlang'ich dasturlash"
    assert ru["sections"][0]["description"] == "Ввод и вывод"
    assert ru["sections"][1]["title"] == "Integer" and ru["sections"][1]["locale"] == "uz"
    page = client.get("/api/v1/roadmaps/abramyan/sections/1/?lang=ru").json()
    assert page["steps"][0]["title"] == "Begin1. Название"
    assert page["steps"][1]["title"] == "Begin2. Nom"
    kaa = client.get("/api/v1/roadmaps/abramyan/?lang=kaa").json()
    assert kaa["locale"] == "kaa"


def test_a_plan_without_sections_keeps_its_steps(user, problem) -> None:
    roadmap = Roadmap.objects.create(slug="plain", title="Plain", is_published=True)
    RoadmapStep.objects.create(roadmap=roadmap, order=1, problem=problem)
    body = APIClient().get("/api/v1/roadmaps/plain/").json()
    assert body["sections"] == [] and [s["problem"] for s in body["steps"]] == [problem.slug]


def test_staff_cannot_replace_a_sectioned_plans_steps(plan) -> None:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff1", password="x", is_staff=True))
    response = client.patch("/api/v1/staff/roadmaps/abramyan/", {"steps": []}, format="json")
    assert response.status_code == 400
    assert RoadmapStep.objects.filter(roadmap=plan).count() == 3
