"""Sinf a'zoligi va progress."""

from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from classroom.models import (
    Assignment,
    Classroom,
    ClassroomJoinRequest,
    ClassroomMember,
    new_code,
)
from core import quotas
from core.models import User


class ClassroomError(Exception):
    """Sinf amali bajarilmadi."""

    def __init__(self, message: str, error: str = "classroom_error") -> None:
        super().__init__(message)
        #: The API error code (`error.<code>` on the site); not a notification code.
        self.code = error


#: A declined student may ask again after this pause.
ASK_AGAIN_AFTER = timedelta(days=1)

#: Who manages a classroom with its owner: approves requests, sees reports.
MANAGERS = (ClassroomMember.Role.ASSISTANT,)


def role_of(classroom: Classroom, user: User) -> str:
    """`owner`, `assistant`, `student` or `""` for this user in this classroom."""
    if classroom.owner_id == user.pk:
        return "owner"
    member = classroom.members.filter(user=user).values_list("role", flat=True).first()
    return str(member or "")


def manages(classroom: Classroom, user: User) -> bool:
    """The owner or an assistant."""
    return role_of(classroom, user) in ("owner", ClassroomMember.Role.ASSISTANT)


def students(classroom: Classroom) -> int:
    return classroom.members.filter(role=ClassroomMember.Role.STUDENT).count()


def check_room(classroom: Classroom) -> None:
    """Refuse one more student past the owner's plan (ADR-0061 § 3)."""
    try:
        quotas.check(classroom.owner, "class_members", students(classroom))
    except quotas.QuotaExceeded as exc:
        raise ClassroomError(
            f"Classroom is full (max {exc.limit})", error="classroom_full"
        ) from exc


def _notify(
    users: list[User], code: str, classroom: Classroom, *, link: bool = True, **params: str
) -> None:
    # Through the service only: `notifications.models` is another app's
    # model (ADR-0042); "system" is `Notification.Kind.SYSTEM`. `link=False`
    # for a reader who cannot open the classroom (a declined request).
    from notifications.services import notify

    for user in users:
        notify(
            user,
            "system",
            code=code,
            params={"classroom": classroom.name, **params},
            ref_type="classroom" if link else "",
            ref_id=classroom.slug if link else "",
        )


def _managers(classroom: Classroom) -> list[User]:
    assistants = User.objects.filter(
        classroom_memberships__classroom=classroom,
        classroom_memberships__role__in=MANAGERS,
    )
    return [classroom.owner, *assistants]


@transaction.atomic
def join(user: User, join_code: str) -> ClassroomMember | ClassroomJoinRequest:
    """A member at once, or a pending request when the classroom asks for approval."""
    try:
        classroom = Classroom.objects.select_for_update().get(join_code=join_code, is_active=True)
    except Classroom.DoesNotExist:
        raise ClassroomError("Classroom not found or inactive", error="join_failed") from None

    if classroom.owner_id == user.pk:
        raise ClassroomError("You already own this classroom", error="join_failed")
    member = classroom.members.filter(user=user).first()
    if member is not None:
        return member

    if classroom.join_mode == Classroom.JoinMode.INSTANT:
        check_room(classroom)
        member, _ = ClassroomMember.objects.get_or_create(classroom=classroom, user=user)
        return member

    # A full classroom still queues the request: the room is checked when the
    # teacher approves, after a seat may have been freed.
    request, created = ClassroomJoinRequest.objects.get_or_create(classroom=classroom, user=user)
    if not created and request.status != ClassroomJoinRequest.Status.PENDING:
        if request.decided_at is not None and timezone.now() - request.decided_at < ASK_AGAIN_AFTER:
            # Without a pause a declined student could ring every manager
            # once per request.
            raise ClassroomError("This request is already answered", error="request_answered")
        # Asking again after the pause reopens the request.
        request.status = ClassroomJoinRequest.Status.PENDING
        request.decided_at = None
        request.decided_by = None
        request.save(update_fields=["status", "decided_at", "decided_by"])
        created = True
    if created:
        _notify(_managers(classroom), "classroom_join_requested", classroom, user=user.username)
    return request


@transaction.atomic
def decide(actor: User, request_id: int, *, approve: bool) -> ClassroomJoinRequest:
    """The owner or an assistant answers a pending request."""
    found = ClassroomJoinRequest.objects.filter(pk=request_id).values_list(
        "classroom_id", flat=True
    )
    classroom_id = found.first()
    if classroom_id is None:
        raise ClassroomError("Request not found", error="request_not_found")
    # The classroom is locked before the request, in the same order as
    # `join()`, so the two cannot deadlock.
    classroom = Classroom.objects.select_for_update().get(pk=classroom_id)
    request = (
        ClassroomJoinRequest.objects.select_for_update().select_related("user").get(pk=request_id)
    )
    if not manages(classroom, actor):
        raise ClassroomError("Request not found", error="request_not_found")
    if request.status != ClassroomJoinRequest.Status.PENDING:
        raise ClassroomError("This request is already answered", error="request_answered")
    if approve:
        check_room(classroom)
        ClassroomMember.objects.get_or_create(classroom=classroom, user=request.user)
    request.status = (
        ClassroomJoinRequest.Status.APPROVED if approve else ClassroomJoinRequest.Status.REJECTED
    )
    request.decided_at = timezone.now()
    request.decided_by = actor
    request.save(update_fields=["status", "decided_at", "decided_by"])
    _notify(
        [request.user],
        "classroom_join_approved" if approve else "classroom_join_rejected",
        classroom,
        link=approve,
    )
    return request


def remove(classroom: Classroom, username: str) -> None:
    """The owner takes a member out.

    Their request is marked declined, so in an approval classroom they cannot
    ask straight back in; an instant classroom needs a new code for that.
    """
    member = classroom.members.filter(user__username=username).select_related("user").first()
    if member is None:
        raise ClassroomError("Not a member", error="not_a_member")
    member.delete()
    ClassroomJoinRequest.objects.update_or_create(
        classroom=classroom,
        user=member.user,
        defaults={
            "status": ClassroomJoinRequest.Status.REJECTED,
            "decided_at": timezone.now(),
            "decided_by": classroom.owner,
        },
    )


def leave(classroom: Classroom, user: User) -> None:
    """A member leaves; the owner cannot."""
    if classroom.owner_id == user.pk:
        raise ClassroomError("The owner cannot leave; archive the classroom", error="owner_leaves")
    deleted, _ = classroom.members.filter(user=user).delete()
    if not deleted:
        raise ClassroomError("Not a member", error="not_a_member")
    ClassroomJoinRequest.objects.filter(classroom=classroom, user=user).delete()


def set_role(classroom: Classroom, username: str, role: str) -> ClassroomMember:
    """The owner makes a member an assistant or a student again."""
    if role not in ClassroomMember.Role.values:
        raise ClassroomError(f"Unknown role: {role}", error="bad_role")
    member = classroom.members.filter(user__username=username).first()
    if member is None:
        raise ClassroomError("Not a member", error="not_a_member")
    if role == ClassroomMember.Role.STUDENT and member.role != role:
        check_room(classroom)
    member.role = role
    member.save(update_fields=["role"])
    return member


def refresh_code(classroom: Classroom) -> str:
    """A new join code: the old one, and every invite link with it, stops working."""
    for _ in range(5):
        code = new_code()
        if not Classroom.objects.filter(join_code=code).exists():
            classroom.join_code = code
            classroom.save(update_fields=["join_code"])
            return code
    raise ClassroomError("Could not make a new code, try again", error="code_failed")


def assignment_progress(assignment: Assignment) -> list[dict[str, object]]:
    """Har o'quvchi bo'yicha nechta masala yechilgan.

    `UserSolvedProblem` dan o'qiydi: uy vazifasi uchun ALOHIDA yechilganlik
    hisobi yuritilmaydi — bir masalani ikki marta yechib bo'lmaydi va
    ikkita haqiqat manbai bo'lishi kerak emas.
    """
    from django.db.models import Count

    from ratings.models import UserSolvedProblem

    problem_ids = list(assignment.problems.values_list("pk", flat=True))
    total = len(problem_ids)
    members = list(
        assignment.classroom.members.filter(role=ClassroomMember.Role.STUDENT).select_related(
            "user"
        )
    )
    if not problem_ids or not members:
        return [{"username": m.user.username, "solved": 0, "total": total} for m in members]

    counts = dict(
        UserSolvedProblem.objects.filter(
            user_id__in=[m.user_id for m in members], problem_id__in=problem_ids
        )
        .values_list("user_id")
        .annotate(n=Count("pk"))
        .values_list("user_id", "n")
    )

    return [
        {
            "username": m.user.username,
            "solved": counts.get(m.user_id, 0),
            "total": total,
        }
        for m in members
    ]


def pending_assignments(user: User) -> int:
    """Assignments a student still has work in: not past due, not all solved.

    Read from `UserSolvedProblem`, as `assignment_progress` is - an
    assignment keeps no completion record of its own. A course given to the
    class is pending until the student's enrolment is complete (a priced
    course the student has not unlocked yet is pending too).
    """
    from django.db.models import Q
    from django.utils import timezone

    from ratings.models import UserSolvedProblem

    rows = list(
        Assignment.objects.filter(
            classroom__is_active=True,
            classroom__members__user=user,
            classroom__members__role=ClassroomMember.Role.STUDENT,
        )
        .filter(Q(due_at__isnull=True) | Q(due_at__gt=timezone.now()))
        .values_list("pk", "problems__pk", "course_id")
    )
    wanted: dict[int, set[int]] = {}
    courses: dict[int, int] = {}
    for assignment_id, problem_id, course_id in rows:
        if problem_id is not None:
            wanted.setdefault(assignment_id, set()).add(problem_id)
        if course_id is not None:
            courses[assignment_id] = course_id
    if not wanted and not courses:
        return 0
    solved = set(
        UserSolvedProblem.objects.filter(
            user=user, problem_id__in=set().union(set(), *wanted.values())
        ).values_list("problem_id", flat=True)
    )
    finished = set(
        user.enrollments.filter(
            course_id__in=set(courses.values()), completed_at__isnull=False
        ).values_list("course_id", flat=True)
    )
    return sum(
        1
        for assignment_id in set(wanted) | set(courses)
        if wanted.get(assignment_id, set()) - solved
        or (assignment_id in courses and courses[assignment_id] not in finished)
    )
