"""Coach links: ask, answer, end, consent, recommend (ADR-0061 § 4)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from coaching.models import CoachLink, Recommendation
from core.models import User

#: Active and pending coaches one student may have (owner decision 2026-11-11).
MAX_COACHES = 3
#: A declined student may ask the same coach again after this pause.
ASK_AGAIN_AFTER = timedelta(days=1)

OPEN = (CoachLink.Status.PENDING, CoachLink.Status.ACTIVE)


class CoachingError(Exception):
    def __init__(self, message: str, error: str) -> None:
        super().__init__(message)
        #: The API error code (`error.<code>` on the site), not a notification code.
        self.code = error


def _notify(to: User, code: str, **params: str) -> None:
    from notifications.services import notify

    notify(to, "system", code=code, params=params, ref_type="coaching", ref_id="")


@transaction.atomic
def ask(student: User, coach_username: str) -> CoachLink:
    """The student asks someone to coach them."""
    coach = User.objects.filter(username=coach_username, is_active=True).first()
    if coach is None:
        raise CoachingError("No such user", error="coach_not_found")
    if coach.pk == student.pk:
        raise CoachingError("You cannot coach yourself", error="coach_self")
    # Lock the student's links: two parallel requests must not pass the cap.
    mine = list(CoachLink.objects.select_for_update().filter(student=student))
    link = next((row for row in mine if row.coach_id == coach.pk), None)
    if link is not None and link.status in OPEN:
        raise CoachingError("Already asked", error="coach_already")
    if sum(1 for row in mine if row.status in OPEN) >= MAX_COACHES:
        raise CoachingError(f"At most {MAX_COACHES} coaches", error="coach_limit")
    if link is not None:
        # After a decline, or after the student withdrew, a pause before the
        # next request: otherwise ask → withdraw → ask rings the coach once
        # per round.
        closed_at = link.ended_at or link.decided_at
        if closed_at is not None and timezone.now() - closed_at < ASK_AGAIN_AFTER:
            raise CoachingError("This coach has answered", error="request_answered")

    consent = bool(student.coach_can_view_attempts)
    if link is None:
        link = CoachLink.objects.create(student=student, coach=coach, can_view_attempts=consent)
    else:
        link.status = CoachLink.Status.PENDING
        link.can_view_attempts = consent
        link.decided_at = None
        link.ended_at = None
        link.save(update_fields=["status", "can_view_attempts", "decided_at", "ended_at"])
    _notify(coach, "coach_requested", user=student.username)
    return link


@transaction.atomic
def answer(coach: User, link_id: int, *, accept: bool) -> CoachLink:
    link = (
        CoachLink.objects.select_for_update()
        .select_related("student")
        .filter(pk=link_id, coach=coach)
        .first()
    )
    if link is None:
        raise CoachingError("Request not found", error="request_not_found")
    if link.status != CoachLink.Status.PENDING:
        raise CoachingError("This request is already answered", error="request_answered")
    link.status = CoachLink.Status.ACTIVE if accept else CoachLink.Status.REJECTED
    link.decided_at = timezone.now()
    link.save(update_fields=["status", "decided_at"])
    _notify(link.student, "coach_accepted" if accept else "coach_declined", user=coach.username)
    return link


def _own_link(user: User, link_id: int) -> CoachLink:
    link = CoachLink.objects.filter(pk=link_id).first()
    if link is None or user.pk not in (link.student_id, link.coach_id):
        raise CoachingError("Not found", error="request_not_found")
    return link


def end(user: User, link_id: int) -> CoachLink:
    """Either side ends the link; a student also withdraws a pending request."""
    link = _own_link(user, link_id)
    if link.status not in OPEN:
        raise CoachingError("Already ended", error="coach_ended")
    link.status = CoachLink.Status.ENDED
    link.ended_at = timezone.now()
    link.save(update_fields=["status", "ended_at"])
    return link


def set_consent(student: User, link_id: int, allowed: bool) -> CoachLink:
    """Only the student decides whether this coach opens their code."""
    link = CoachLink.objects.filter(pk=link_id, student=student).first()
    if link is None:
        raise CoachingError("Not found", error="request_not_found")
    link.can_view_attempts = allowed
    link.save(update_fields=["can_view_attempts"])
    return link


def recommend(coach: User, link_id: int, problem_ref: str, note: str = "") -> Recommendation:
    from problems.lookup import public_problem

    link = (
        CoachLink.objects.select_related("student")
        .filter(pk=link_id, coach=coach, status=CoachLink.Status.ACTIVE)
        .first()
    )
    if link is None:
        raise CoachingError("Not your student", error="request_not_found")
    problem = public_problem(problem_ref)
    if problem is None:
        raise CoachingError(f"Not found: {problem_ref}", error="coach_problem_missing")
    row, created = Recommendation.objects.get_or_create(
        link=link, problem=problem, defaults={"note": note.strip()}
    )
    if created:
        _notify(link.student, "coach_recommended", user=coach.username, problem=problem.title)
    return row


def recommendations_for(student: User) -> list[dict[str, Any]]:
    """Every recommendation from the student's active coaches, solved or not."""
    from ratings.solved import solved_ids

    rows = list(
        Recommendation.objects.filter(
            link__student=student, link__status=CoachLink.Status.ACTIVE
        ).select_related("problem", "link__coach")
    )
    done = solved_ids(student.pk, [row.problem_id for row in rows])
    return [
        {
            "id": row.pk,
            "coach": row.link.coach.username,
            "problem": row.problem.slug,
            "problem_title": row.problem.title,
            "note": row.note,
            "solved": row.problem_id in done,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def students_of(coach: User) -> list[dict[str, Any]]:
    """The coach's panel: each active student's progress and latest attempts."""
    from judging.recent import recent_attempts
    from ratings.solved import solved_ids

    links = CoachLink.objects.filter(coach=coach, status=CoachLink.Status.ACTIVE).select_related(
        "student"
    )
    out = []
    for link in links:
        student = link.student
        given = list(link.recommendations.select_related("problem"))
        done = solved_ids(student.pk, [row.problem_id for row in given])
        out.append(
            {
                "link": link.pk,
                "username": student.username,
                "display_name": student.display_name,
                "can_view_attempts": link.can_view_attempts,
                "solved_count": student.solved_count,
                "rating_skills": student.rating_skills,
                "streak": student.streak_count,
                "recent": recent_attempts(student.pk),
                "recommended": [
                    {
                        "problem": row.problem.slug,
                        "problem_title": row.problem.title,
                        "solved": row.problem_id in done,
                    }
                    for row in given
                ],
            }
        )
    return out
