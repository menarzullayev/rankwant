"""A problem's text in other languages (ADR-0058)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from problems import release, translations
from problems.models import Problem, ProblemTranslation

pytestmark = pytest.mark.django_db


def _client(user: User | None = None) -> APIClient:
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


@pytest.fixture
def staff_client(db) -> APIClient:
    return _client(User.objects.create_user("tarjima-staff", password="x", is_staff=True))


@pytest.fixture
def russian(problem: Problem) -> ProblemTranslation:
    return ProblemTranslation.objects.create(
        problem=problem,
        locale="ru",
        title="Сумма двух чисел",
        statement="Найдите сумму.",
        input_format="Два числа.",
        editorial="Сложите.",
    )


def _detail(problem: Problem, lang: str = "") -> dict:
    query = f"?lang={lang}" if lang else ""
    body: dict = _client().get(f"/api/v1/problems/{problem.slug}/{query}").json()
    return body


class TestReading:
    def test_the_readers_language_with_fallback_per_field(self, problem, russian) -> None:
        base = _detail(problem)
        assert (base["title"], base["locale"]) == (problem.title, problem.statement_locale)
        ru = _detail(problem, "ru")
        assert (ru["title"], ru["statement"], ru["input_format"]) == (
            "Сумма двух чисел",
            "Найдите сумму.",
            "Два числа.",
        )
        # Not translated: the author's text, not an empty block.
        assert ru["output_format"] == base["output_format"]
        assert ru["note"] == base["note"]
        assert ru["locale"] == "ru"
        assert ru["locales"] == [problem.statement_locale, "ru"]

    def test_a_missing_language_shows_the_authors_text(self, problem, russian) -> None:
        en = _detail(problem, "en")
        assert (en["title"], en["locale"]) == (problem.title, problem.statement_locale)

    def test_a_locked_editorial_stays_locked(self, problem, russian) -> None:
        Problem.objects.filter(pk=problem.pk).update(editorial="Yechim: qo'shing.")
        assert _detail(problem, "ru")["editorial"] == ""

    def test_the_archive_list_uses_the_readers_title(self, problem, russian) -> None:
        rows = _client().get("/api/v1/problems/?lang=ru").json()["results"]
        assert next(r for r in rows if r["slug"] == problem.slug)["title"] == "Сумма двух чисел"
        rows = _client().get("/api/v1/problems/?lang=en").json()["results"]
        assert next(r for r in rows if r["slug"] == problem.slug)["title"] == problem.title

    def test_the_search_finds_a_translated_title(self, problem, russian) -> None:
        problem.refresh_from_db()
        assert "сумма двух чисел" in problem.translated_titles
        body = _client().get(reverse("search"), {"q": "сумма двух"}).json()
        groups = {group["type"]: group for group in body["groups"]}
        keys = [hit["key"] for hit in groups.get("problem", {}).get("results", [])]
        assert problem.slug in keys

    def test_titles_follow_a_deleted_translation(self, problem, russian) -> None:
        russian.delete()
        problem.refresh_from_db()
        assert problem.translated_titles == ""

    def test_the_release_package_records_translations(self, problem, russian) -> None:
        package = release.snapshot_package(problem)
        rows = package["statement"]["translations"]
        assert [(r["locale"], r["title"]) for r in rows] == [("ru", "Сумма двух чисел")]

    def test_karakalpak_fits_the_authors_language(self, problem) -> None:
        Problem.objects.filter(pk=problem.pk).update(statement_locale="kaa")
        assert _detail(problem)["locale"] == "kaa"


class TestStaffWriting:
    def _url(self, problem: Problem, locale: str = "") -> str:
        base = f"/api/v1/staff/problems/{problem.slug}/translations/"
        return f"{base}{locale}/" if locale else base

    def test_create_replace_list_delete(self, staff_client, problem) -> None:
        body = {"title": "Sum", "statement": "Add them."}
        assert staff_client.put(self._url(problem, "en"), body, format="json").status_code == 201
        again = staff_client.put(
            self._url(problem, "en"), {**body, "title": "Sum of two"}, format="json"
        )
        assert (again.status_code, again.json()["title"]) == (200, "Sum of two")
        assert [r["locale"] for r in staff_client.get(self._url(problem)).json()] == ["en"]
        assert staff_client.delete(self._url(problem, "en")).status_code == 204
        assert not ProblemTranslation.objects.exists()

    def test_the_authors_language_is_refused(self, staff_client, problem) -> None:
        res = staff_client.put(
            self._url(problem, problem.statement_locale), {"title": "x"}, format="json"
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "problem_translation_is_base"

    def test_an_unknown_language_is_not_found(self, staff_client, problem) -> None:
        assert (
            staff_client.put(self._url(problem, "xx"), {"title": "x"}, format="json").status_code
            == 404
        )

    def test_a_title_is_required(self, staff_client, problem) -> None:
        assert (
            staff_client.put(
                self._url(problem, "ru"), {"statement": "x"}, format="json"
            ).status_code
            == 400
        )


class TestAuthorWriting:
    def _draft(self, user: User) -> Problem:
        problem = Problem.objects.create(
            slug="tarjima-draft", title="Yig'indi", statement="a+b", difficulty=800, is_public=False
        )
        problem.authors.add(user)
        return problem

    def _url(self, problem: Problem, locale: str) -> str:
        return f"/api/v1/problems/mine/{problem.slug}/translations/{locale}/"

    def test_the_author_translates_a_draft(self, user) -> None:
        draft = self._draft(user)
        res = _client(user).put(self._url(draft, "ru"), {"title": "Сумма"}, format="json")
        assert res.status_code == 201
        listed = _client(user).get(f"/api/v1/problems/mine/{draft.slug}/translations/").json()
        assert [r["locale"] for r in listed] == ["ru"]

    def test_a_published_problem_is_refused(self, user) -> None:
        draft = self._draft(user)
        Problem.objects.filter(pk=draft.pk).update(is_public=True)
        res = _client(user).put(self._url(draft, "ru"), {"title": "Сумма"}, format="json")
        assert res.status_code == 403

    def test_the_draft_names_its_language_read_only(self, user) -> None:
        draft = self._draft(user)
        url = f"/api/v1/problems/mine/{draft.slug}/"
        assert _client(user).get(url).json()["statement_locale"] == "uz"
        _client(user).patch(url, {"statement_locale": "ru"}, format="json")
        draft.refresh_from_db()
        assert draft.statement_locale == "uz"

    def test_someone_elses_draft_is_not_found(self, user, other_user) -> None:
        draft = self._draft(user)
        res = _client(other_user).put(self._url(draft, "ru"), {"title": "Сумма"}, format="json")
        assert res.status_code == 404


def test_reader_locale_prefers_the_query(rf) -> None:
    from rest_framework.request import Request

    request = Request(rf.get("/x", {"lang": "kaa"}))
    assert translations.reader_locale(request) == "kaa"
    request = Request(rf.get("/x", {"lang": "xx"}))
    assert translations.reader_locale(request) in translations.LOCALES
