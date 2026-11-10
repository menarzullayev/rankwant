"""Course studio and review (ADR-0056, part 4)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from courses import review
from courses.models import (
    Course,
    CourseTranslation,
    Lesson,
    LessonTranslation,
    Module,
    ModuleTranslation,
    Section,
)
from notifications.models import Notification
from quizzes.models import Quiz

pytestmark = pytest.mark.django_db


def _client(user: User | None = None) -> APIClient:
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


@pytest.fixture
def staff(db) -> User:
    return User.objects.create_user(username="xodim", password="Parol!12345", is_staff=True)


def _create(user: User, title: str = "C++ asoslari", **extra) -> dict:
    resp = _client(user).post(
        reverse("studio-course-list"), {"title": title, **extra}, format="json"
    )
    assert resp.status_code == 201, resp.json()
    data: dict = resp.json()
    return data


def _ready_course(author: User, title: str = "C++ asoslari") -> Course:
    """A draft with everything the review asks for."""
    data = _create(author, title=title, summary="Qisqa")
    course = Course.objects.get(slug=data["slug"])
    module = Module.objects.create(course=course, order=1)
    section = Section.objects.create(module=module, order=1)
    lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
    LessonTranslation.objects.create(lesson=lesson, locale="uz", title="Kirish", body="Matn")
    return course


def _text(user, slug, **data):
    return _client(user).post(reverse("studio-course-text", args=[slug]), data, format="json")


class TestDrafts:
    def test_create_makes_a_free_draft_owned_by_the_author(self, user):
        data = _create(user, summary="Qisqa")
        course = Course.objects.get(slug=data["slug"])
        assert data["slug"] == "c-asoslari"
        assert (course.access, course.is_published) == (Course.Access.FREE, False)
        assert list(course.authors.all()) == [user]
        assert course.translations.get().title == "C++ asoslari"
        assert data["status"] == "draft"

    def test_slug_must_be_free(self, user):
        _create(user, slug="kurs")
        resp = _client(user).post(
            reverse("studio-course-list"), {"title": "x", "slug": "kurs"}, format="json"
        )
        assert resp.status_code == 400

    def test_draft_limit_for_authors_not_for_staff(self, user, staff):
        for i in range(review.MAX_DRAFTS):
            _create(user, title=f"Kurs {i}")
        resp = _client(user).post(reverse("studio-course-list"), {"title": "Yana"}, format="json")
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "course_draft_limit"
        for i in range(review.MAX_DRAFTS + 1):
            _create(staff, title=f"Xodim {i}")

    def test_another_users_course_is_invisible(self, user, other_user):
        data = _create(user)
        assert (
            _client(other_user)
            .get(reverse("studio-course-detail", args=[data["slug"]]))
            .status_code
            == 404
        )
        resp = _text(other_user, data["slug"], target="course", locale="uz", title="Buzildi")
        assert resp.status_code == 404
        assert [
            r["slug"]
            for r in _client(other_user).get(reverse("studio-course-list")).json()["results"]
        ] == []

    def test_guest_is_refused(self):
        assert _client().get(reverse("studio-course-list")).status_code in (401, 403)

    def test_author_cannot_set_price(self, user):
        data = _create(user)
        resp = _client(user).patch(
            reverse("studio-course-detail", args=[data["slug"]]),
            {"access": "paid", "price_uzs": 100, "level": "advanced"},
            format="json",
        )
        assert resp.status_code == 200
        course = Course.objects.get(slug=data["slug"])
        assert (course.access, course.price_uzs, course.level) == ("free", 0, "advanced")


class TestText:
    def test_translations_are_written_and_cleared(self, user):
        slug = _create(user)["slug"]
        assert (
            _text(user, slug, target="course", locale="en", title="C++ basics").status_code == 200
        )
        course = Course.objects.get(slug=slug)
        assert course.translations.get(locale="en").title == "C++ basics"
        _text(user, slug, target="course", locale="en", title="")
        assert not course.translations.filter(locale="en").exists()

    def test_base_translation_is_kept_even_when_cleared(self, user):
        slug = _create(user, summary="Qisqa")["slug"]
        _text(user, slug, target="course", locale="uz", title="", summary="")
        assert CourseTranslation.objects.filter(course__slug=slug, locale="uz").exists()

    def test_lesson_text_of_another_course_is_404(self, user):
        mine = _ready_course(user)
        other = _ready_course(user, title="Boshqa kurs")
        lesson = Lesson.objects.get(section__module__course=other)
        resp = _text(user, mine.slug, target="lesson", id=lesson.pk, locale="uz", title="X")
        assert resp.status_code == 404

    def test_author_edits_text_of_a_published_course(self, user):
        course = _ready_course(user)
        Course.objects.filter(pk=course.pk).update(is_published=True)
        lesson = Lesson.objects.get(section__module__course=course)
        resp = _text(
            user,
            course.slug,
            target="lesson",
            id=lesson.pk,
            locale="uz",
            title="Kirish",
            body="Tuzatildi",
        )
        assert resp.status_code == 200
        assert LessonTranslation.objects.get(lesson=lesson, locale="uz").body == "Tuzatildi"


class TestStructure:
    def test_tree_is_built_step_by_step(self, user):
        slug = _create(user)["slug"]
        c = _client(user)
        module = c.post(
            reverse("studio-course-module-list", args=[slug]), {"order": 1}, format="json"
        ).json()
        section = c.post(
            reverse("studio-course-section-list", args=[slug]),
            {"module": module["id"]},
            format="json",
        ).json()
        lesson = c.post(
            reverse("studio-course-lesson-list", args=[slug]),
            {
                "section": section["id"],
                "kind": "video",
                "video_provider": "youtube",
                "video_ref": "dQw4w9WgXcQ",
            },
            format="json",
        )
        assert lesson.status_code == 201, lesson.json()
        _text(user, slug, target="module", id=module["id"], locale="uz", title="Kirish")
        tree = c.get(reverse("studio-course-detail", args=[slug])).json()
        assert tree["modules"][0]["texts"] == [{"locale": "uz", "title": "Kirish"}]
        assert tree["modules"][0]["sections"][0]["lessons"][0]["kind"] == "video"
        assert ModuleTranslation.objects.count() == 1

    def test_section_of_another_course_is_refused(self, user):
        mine = _create(user, title="Bir")["slug"]
        other = _ready_course(user, title="Boshqa kurs")
        section = Section.objects.get(module__course=other)
        resp = _client(user).post(
            reverse("studio-course-lesson-list", args=[mine]),
            {"section": section.pk},
            format="json",
        )
        assert resp.status_code == 400

    def test_published_structure_is_staffs(self, user, staff):
        course = _ready_course(user)
        Course.objects.filter(pk=course.pk).update(is_published=True)
        url = reverse("studio-course-module-list", args=[course.slug])
        resp = _client(user).post(url, {"order": 2}, format="json")
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "course_structure_locked"
        lesson = Lesson.objects.get(section__module__course=course)
        delete = _client(user).delete(
            reverse("studio-course-lesson-detail", args=[course.slug, lesson.pk])
        )
        assert delete.status_code == 403
        assert _client(staff).post(url, {"order": 2}, format="json").status_code == 201

    def test_published_course_is_not_deleted(self, user):
        course = _ready_course(user)
        Course.objects.filter(pk=course.pk).update(is_published=True)
        assert (
            _client(user).delete(reverse("studio-course-detail", args=[course.slug])).status_code
            == 403
        )
        assert Course.objects.filter(pk=course.pk).exists()

    def test_draft_is_deleted(self, user):
        slug = _create(user)["slug"]
        assert _client(user).delete(reverse("studio-course-detail", args=[slug])).status_code == 204

    def test_author_cannot_set_a_qvant_reward(self, user, staff):
        slug = _create(user)["slug"]
        url = reverse("studio-course-module-list", args=[slug])
        assert _client(user).post(url, {"reward_qvant": 50}, format="json").status_code == 400
        assert _client(staff).post(url, {"reward_qvant": 50}, format="json").status_code == 201

    def test_paid_course_refuses_a_youtube_video(self, user):
        course = _ready_course(user)
        Course.objects.filter(pk=course.pk).update(access=Course.Access.PAID, price_uzs=1000)
        section = Section.objects.get(module__course=course)
        resp = _client(user).post(
            reverse("studio-course-lesson-list", args=[course.slug]),
            {"section": section.pk, "kind": "video", "video_provider": "youtube", "video_ref": "x"},
            format="json",
        )
        assert resp.status_code == 400


class TestReview:
    def test_gaps_are_named(self, user):
        slug = _create(user)["slug"]
        resp = _client(user).post(reverse("studio-course-review", args=[slug]))
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "course_review_not_ready"
        assert set(resp.json()["error"]["details"]["missing"]) == {"summary", "lessons"}

    def test_lesson_gaps(self, user, problem):
        course = _ready_course(user)
        section = Section.objects.get(module__course=course)
        Lesson.objects.create(section=section, order=2, kind=Lesson.Kind.QUIZ)
        hidden = Lesson.objects.create(
            section=section, order=3, kind=Lesson.Kind.PROBLEM, problem=problem
        )
        problem.is_public = False
        problem.save(update_fields=["is_public"])
        assert review.review_gaps(course) == ["lesson_title", "lesson_quiz", "lesson_problem"]
        assert hidden.pk

    def test_request_tells_staff_once(self, user, staff):
        course = _ready_course(user)
        url = reverse("studio-course-review", args=[course.slug])
        assert _client(user).post(url).json()["status"] == "review"
        _client(user).post(url)
        notes = Notification.objects.filter(user=staff, code="course_review_requested")
        assert notes.count() == 1
        assert notes.get().params["course"] == "C++ asoslari"

    def test_staff_queue_and_publish(self, user, staff):
        course = _ready_course(user)
        _client(user).post(reverse("studio-course-review", args=[course.slug]))
        queue = _client(staff).get(reverse("staff-course-list"), {"review": "1"}).json()["results"]
        assert [row["slug"] for row in queue] == [course.slug]
        resp = _client(staff).post(reverse("staff-course-publish", args=[course.slug]))
        assert resp.status_code == 200
        course.refresh_from_db()
        assert course.is_published and course.published_at and course.review_requested_at is None
        assert Notification.objects.filter(user=user, code="course_published").count() == 1

    def test_send_back_with_reason(self, user, staff):
        course = _ready_course(user)
        _client(user).post(reverse("studio-course-review", args=[course.slug]))
        resp = _client(staff).post(
            reverse("staff-course-send-back", args=[course.slug]),
            {"reason": "Misollar kam"},
            format="json",
        )
        assert resp.status_code == 200
        course.refresh_from_db()
        assert course.review_requested_at is None and not course.is_published
        note = Notification.objects.get(user=user, code="course_returned")
        assert note.params["reason"] == "Misollar kam"

    def test_staff_prices_the_course(self, user, staff):
        course = _ready_course(user)
        url = reverse("staff-course-detail", args=[course.slug])
        assert _client(staff).patch(url, {"access": "paid"}, format="json").status_code == 400
        resp = _client(staff).patch(url, {"access": "qvant", "price_qvant": 200}, format="json")
        assert resp.status_code == 200
        assert Course.objects.get(pk=course.pk).price_qvant == 200

    def test_pricing_refuses_shareable_video(self, user, staff):
        course = _ready_course(user)
        section = Section.objects.get(module__course=course)
        Lesson.objects.create(
            section=section,
            order=2,
            kind=Lesson.Kind.VIDEO,
            video_provider="youtube",
            video_ref="x",
        )
        resp = _client(staff).patch(
            reverse("staff-course-detail", args=[course.slug]),
            {"access": "paid", "price_uzs": 50000},
            format="json",
        )
        assert resp.status_code == 400
        assert Course.objects.get(pk=course.pk).access == Course.Access.FREE

    def test_authors_cannot_use_staff_endpoints(self, user):
        course = _ready_course(user)
        assert _client(user).get(reverse("staff-course-list")).status_code == 403
        assert (
            _client(user).post(reverse("staff-course-publish", args=[course.slug])).status_code
            == 403
        )

    def test_final_quiz_by_slug(self, user):
        quiz = Quiz.objects.create(slug="yakuniy", title="Yakuniy", is_published=True)
        slug = _create(user)["slug"]
        resp = _client(user).patch(
            reverse("studio-course-detail", args=[slug]), {"final_quiz": "yakuniy"}, format="json"
        )
        assert resp.status_code == 200
        assert Course.objects.get(slug=slug).final_quiz == quiz


class TestVideoReference:
    @pytest.mark.parametrize(
        ("provider", "pasted", "stored"),
        [
            ("youtube", "dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtube", "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10", "dQw4w9WgXcQ"),
            ("youtube", "https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("youtube", "youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("vimeo", "https://vimeo.com/76979871", "76979871"),
            ("vimeo", "https://player.vimeo.com/video/76979871?h=x", "76979871"),
        ],
    )
    def test_links_are_reduced_to_the_id(self, provider, pasted, stored):
        from courses.video import normalise

        assert normalise(provider, pasted) == stored

    @pytest.mark.parametrize(
        ("provider", "pasted"),
        [
            ("youtube", "https://evil.example/watch?v=dQw4w9WgXcQ"),
            ("youtube", 'dQw4w9WgXcQ"><script>'),
            ("vimeo", "https://vimeo.com/abc"),
            ("hls", "../other-course/master"),
        ],
    )
    def test_anything_else_is_refused(self, provider, pasted):
        from courses.video import normalise

        with pytest.raises(ValueError):
            normalise(provider, pasted)

    def test_studio_stores_the_id(self, user):
        course = _ready_course(user)
        section = Section.objects.get(module__course=course)
        resp = _client(user).post(
            reverse("studio-course-lesson-list", args=[course.slug]),
            {
                "section": section.pk,
                "kind": "video",
                "video_provider": "youtube",
                "video_ref": "https://youtu.be/dQw4w9WgXcQ",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.json()
        assert resp.json()["video_ref"] == "dQw4w9WgXcQ"

    def test_author_cannot_type_an_r2_key(self, user, staff):
        course = _ready_course(user)
        section = Section.objects.get(module__course=course)
        data = {
            "section": section.pk,
            "kind": "video",
            "video_provider": "hls",
            "video_ref": "videos/x/master",
        }
        url = reverse("studio-course-lesson-list", args=[course.slug])
        assert _client(user).post(url, data, format="json").status_code == 400
        assert _client(staff).post(url, data, format="json").status_code == 201
