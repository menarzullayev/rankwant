"""Part 2 of the notification parity work: the emitters (decision 2026-11-16)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from classroom import services as classroom_services
from classroom.models import Classroom, ClassroomMember
from contests import reminders as contest_reminders
from contests.models import Contest
from contests.staff_views import StaffContestViewSet
from core.models import User
from notifications import groups, reminders
from notifications.models import Notification, ReminderSent


def _person(name: str, *, seen: bool = True) -> User:
    user = User.objects.create_user(username=name, password="Parol!12345", email=f"{name}@rw.uz")
    if seen:
        User.objects.filter(pk=user.pk).update(last_seen_at=timezone.now())
    return user


@pytest.mark.django_db
class TestClassroom:
    def test_the_teacher_hears_when_a_student_leaves(self) -> None:
        teacher, pupil = _person("ustoz"), _person("oquvchi")
        room = Classroom.objects.create(owner=teacher, name="9-A", slug="9a")
        ClassroomMember.objects.create(classroom=room, user=pupil)
        classroom_services.leave(room, pupil)
        row = Notification.objects.get(user=teacher, code="my_class_student_left")
        assert row.params["user"] == "oquvchi" and row.params["classroom"] == "9-A"


@pytest.mark.django_db
class TestNewContest:
    def test_active_people_hear_once_and_the_sleeping_do_not(self) -> None:
        awake, asleep = _person("faol"), _person("uxlagan", seen=False)
        first = reminders.announce_to_active(
            "contest_new", "contest:1", "contest", "kuz-kubogi", contest="Kuz kubogi"
        )
        again = reminders.announce_to_active(
            "contest_new", "contest:1", "contest", "kuz-kubogi", contest="Kuz kubogi"
        )
        assert first == 1 and again == 0
        assert Notification.objects.filter(user=awake, code="contest_new").count() == 1
        assert not Notification.objects.filter(user=asleep).exists()
        assert ReminderSent.objects.filter(user=awake, code="contest_new").count() == 1

    def test_only_a_publication_announces(self, monkeypatch: pytest.MonkeyPatch) -> None:
        queued: list[int] = []
        monkeypatch.setattr("core.tasks.queue", lambda task, pk: queued.append(pk))
        public = Contest(pk=7, slug="k", title="K", is_public=True)
        StaffContestViewSet._announce_if_new(public, was_public=True)
        assert queued == []
        StaffContestViewSet._announce_if_new(Contest(pk=7, is_public=False), was_public=False)
        assert queued == []
        StaffContestViewSet._announce_if_new(public, was_public=False)
        assert queued == [7]


@pytest.mark.django_db
class TestPlagiarismNotice:
    def _ended(self, slug: str, host: User) -> Contest:
        now = timezone.now()
        contest = Contest.objects.create(
            slug=slug,
            title="Tugagan",
            start_at=now - timedelta(hours=4),
            end_at=now - timedelta(minutes=30),
        )
        contest.organizers.add(host)
        return contest

    def test_the_host_hears_how_many_people_were_flagged_once(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        host = _person("tashkilotchi")
        self._ended("ended", host)
        monkeypatch.setattr(
            "contests.integrity.report",
            lambda c: [{"username": "a"}, {"username": "a"}, {"username": "b"}],
        )
        contest_reminders.plagiarism_found()
        contest_reminders.plagiarism_found()
        row = Notification.objects.get(user=host, code="host_plagiarism_found")
        assert row.params["count"] == "2"

    def test_no_flags_no_notice(self, monkeypatch: pytest.MonkeyPatch) -> None:
        host = _person("tashkilotchi2")
        self._ended("clean", host)
        monkeypatch.setattr("contests.integrity.report", lambda c: [])
        contest_reminders.plagiarism_found()
        assert not Notification.objects.filter(user=host, code="host_plagiarism_found").exists()


class TestDormant:
    def test_codes_without_an_event_stay_hidden_from_settings(self) -> None:
        for code in ("class_invited", "problem_archived", "contest_rating_reverted"):
            assert code in groups.DORMANT
        visible = groups.visible_groups()
        assert "new_contests" in visible and "my_content" in visible
        assert "team_prizes" not in visible
