"""Bildirishnomalar — PRD P1-4 va ADR-0007 majburiyati."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from judging.models import Attempt
from judging.services import apply_result
from notifications.models import Notification
from notifications.services import mark_read, notify, notify_many, unread_count


@pytest.mark.django_db
class TestService:
    def test_yaratish(self, user) -> None:
        n = notify(user, Notification.Kind.SYSTEM, "Salom")
        assert n is not None and not n.is_read

    def test_guruhga(self, user, other_user) -> None:
        assert notify_many([user, other_user], Notification.Kind.SYSTEM, "Yangilik") == 2

    def test_bosh_guruh(self) -> None:
        assert notify_many([], Notification.Kind.SYSTEM, "x") == 0

    def test_oqilgan_deb_belgilash(self, user) -> None:
        notify(user, Notification.Kind.SYSTEM, "a")
        notify(user, Notification.Kind.SYSTEM, "b")
        assert unread_count(user) == 2
        assert mark_read(user) == 2
        assert unread_count(user) == 0

    def test_tanlab_belgilash(self, user) -> None:
        first = notify(user, Notification.Kind.SYSTEM, "a")
        notify(user, Notification.Kind.SYSTEM, "b")
        assert first is not None
        mark_read(user, [first.pk])
        assert unread_count(user) == 1


@pytest.mark.django_db
class TestRatingNotifications:
    def test_qayta_baholash_xabar_beradi(self, user, problem, language) -> None:
        """ADR-0007 sharti: reyting o'z harakatisiz o'zgarsa — xabar."""
        from ratings.services import recalc_skills_for_problem

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        Notification.objects.all().delete()  # AC dan kelganini tozalaymiz

        problem.difficulty = 1500
        problem.save()
        recalc_skills_for_problem(problem.pk)

        note = Notification.objects.get(user=user, kind=Notification.Kind.PROBLEM_RERATED)
        assert "+700" in note.title
        assert "harakatingiz emas" in note.body

    def test_oddiy_yechish_qayta_baholash_xabarini_bermaydi(self, user, problem, language) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        assert not Notification.objects.filter(kind=Notification.Kind.PROBLEM_RERATED).exists()

    def test_contest_natijasi_xabar_beradi(self, contest, problem, language) -> None:
        from contests.services import finalize_contest
        from core.models import User

        for i in range(10):
            u = User.objects.create_user(username=f"n{i}", password="Parol!12345")
            a = Attempt.objects.create(
                user=u,
                problem=problem,
                contest=contest,
                language=language,
                source_code="x",
                verdict="AC",
            )
            Attempt.objects.filter(pk=a.pk).update(created_at=contest.start_at)
        finalize_contest(contest)
        assert Notification.objects.filter(kind=Notification.Kind.CONTEST_RESULT).count() == 10


@pytest.mark.django_db
class TestApi:
    def _client(self, user) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    def test_royxat(self, user) -> None:
        notify(user, Notification.Kind.SYSTEM, "Salom")
        body = self._client(user).get(reverse("notification-list")).json()
        assert body["results"][0]["title"] == "Salom"

    def test_faqat_oqilmaganlar(self, user) -> None:
        first = notify(user, Notification.Kind.SYSTEM, "a")
        notify(user, Notification.Kind.SYSTEM, "b")
        assert first is not None
        mark_read(user, [first.pk])
        body = self._client(user).get(reverse("notification-list"), {"unread": "true"}).json()
        assert len(body["results"]) == 1

    def test_oqilmagan_soni(self, user) -> None:
        notify(user, Notification.Kind.SYSTEM, "a")
        body = self._client(user).get(reverse("notification-unread-count")).json()
        assert body["count"] == 1

    def test_belgilash_endpointi(self, user) -> None:
        notify(user, Notification.Kind.SYSTEM, "a")
        r = self._client(user).post(reverse("notification-mark-read"), {}, format="json")
        assert r.json()["updated"] == 1

    def test_boshqa_foydalanuvchi_kormaydi(self, user, other_user) -> None:
        notify(user, Notification.Kind.SYSTEM, "MAXFIY")
        body = self._client(other_user).get(reverse("notification-list")).json()
        assert body["results"] == []
