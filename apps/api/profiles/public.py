"""Ommaviy profil — ma'lumot, faoliyat, yutuqlar, xaridlar.

Maxfiylik qoidasi bitta joyda: `hidden_fields` dagi maydon egasidan
boshqa hech kimga ko'rinmaydi. Qolgani — standart bo'yicha ochiq
(foydalanuvchi shuni tanladi, yashirish uning o'z qo'lida).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from core.models import User
from profiles.catalog import TECHNOLOGIES
from profiles.models import (
    Education,
    ExternalProfile,
    Follow,
    UserSkill,
    UserTechnology,
    WorkExperience,
)

#: «Qiyin masala yechildi» voqeasi shu qiyinlikdan boshlanadi (`upper` darajasi).
HARD_FROM = 1800
SOLVE_MILESTONES = (1, 10, 100, 500, 1000)
STREAK_MILESTONES = ((7, "streak_7"), (30, "streak_30"), (365, "streak_365"))
CONTEST_MILESTONES = (1, 10, 50)


def build_profile(user: User, viewer: User | None) -> dict[str, Any]:
    from qvant.services import equipped

    owner = viewer is not None and viewer.pk == user.pk
    hidden = set(user.hidden_fields or [])

    def visible(field: str) -> bool:
        return owner or field not in hidden

    info: dict[str, Any] = {}
    if visible("email") and user.email:
        info["email"] = user.email
    if visible("birth_date") and user.birth_date:
        info["birth_date"] = user.birth_date.isoformat()
    if visible("country") and user.country:
        info["country"] = user.country
        if user.region:
            info["region"] = user.region
    for field in ("school", "grade", "website"):
        value = getattr(user, field)
        if visible(field) and value:
            info[field] = value

    return {
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "date_joined": user.date_joined,
        "info": info,
        "hidden_fields": sorted(hidden) if owner else [],
        "is_owner": owner,
        "skills": [
            {
                "slug": row.skill.slug,
                "name_uz": row.skill.name_uz,
                "name_ru": row.skill.name_ru,
                "name_en": row.skill.name_en,
                "level": row.level,
            }
            for row in UserSkill.objects.filter(user=user).select_related("skill")
        ],
        "technologies": [
            {"slug": row.slug, "name": TECHNOLOGIES.get(row.slug, row.slug)}
            for row in UserTechnology.objects.filter(user=user)
        ],
        "educations": list(
            Education.objects.filter(user=user).values(
                "organization", "degree", "start_year", "end_year"
            )
        ),
        "work": list(
            WorkExperience.objects.filter(user=user).values(
                "company", "title", "start_year", "end_year"
            )
        ),
        "external": list(
            ExternalProfile.objects.filter(user=user).values(
                "kind", "handle", "rating", "max_rating", "rank"
            )
        ),
        "followers": Follow.objects.filter(following=user).count(),
        "following": Follow.objects.filter(follower=user).count(),
        "is_following": (
            Follow.objects.filter(follower=viewer, following=user).exists()
            if viewer is not None and not owner
            else None
        ),
        "cosmetics": equipped(user),
    }


def activity(user: User, *, before: datetime | None = None, limit: int = 30) -> dict[str, Any]:
    """Voqealar lentasi: musobaqa, bajarilgan vazifa, qiyin masala.

    Uch jadvaldan yig'iladi va vaqt bo'yicha birlashtiriladi. Keyingi
    sahifa — oxirgi voqea vaqtidan oldingilar (`next_before`).
    """
    from qvant.models import UserQuestCompletion
    from ratings.models import RatingHistory, UserSolvedProblem

    contests = RatingHistory.objects.filter(user=user, reason=RatingHistory.Reason.CONTEST)
    quests = UserQuestCompletion.objects.filter(user=user).select_related("quest")
    solves = UserSolvedProblem.objects.filter(
        user=user, difficulty_at_solve__gte=HARD_FROM, problem__is_public=True
    ).select_related("problem")
    if before is not None:
        contests = contests.filter(created_at__lt=before)
        quests = quests.filter(completed_at__lt=before)
        solves = solves.filter(first_ac_at__lt=before)

    events: list[dict[str, Any]] = [
        {
            "type": "contest",
            "at": row.created_at,
            "ref": row.ref_id,
            "delta": row.delta,
            "value_after": row.value_after,
            "rank": row.rank,
        }
        for row in contests.order_by("-created_at")[:limit]
    ]
    events += [
        {
            "type": "quest",
            "at": row.completed_at,
            "code": row.quest.code,
            "title_uz": row.quest.title_uz,
            "title_ru": row.quest.title_ru,
            "title_en": row.quest.title_en,
            "awarded": row.awarded,
        }
        for row in quests.order_by("-completed_at")[:limit]
    ]
    events += [
        {
            "type": "hard_solve",
            "at": row.first_ac_at,
            "ref": row.problem.slug,
            "title": row.problem.title,
            "difficulty": row.difficulty_at_solve,
        }
        for row in solves.order_by("-first_ac_at")[:limit]
    ]
    events.sort(key=lambda e: e["at"], reverse=True)
    page = events[:limit]
    return {
        "results": page,
        "next_before": page[-1]["at"].isoformat() if len(page) == limit else None,
    }


def achievements(user: User) -> list[dict[str, Any]]:
    """Yutuqlar — mavjud ma'lumotdan hisoblanadi, alohida jadval yo'q."""
    from qvant.models import UserQuestCompletion
    from qvant.quests import PROFILE_COMPLETE
    from ratings.models import RatingHistory, UserSolvedProblem

    solved = UserSolvedProblem.objects.filter(user=user).count()
    contests = (
        RatingHistory.objects.filter(user=user, reason=RatingHistory.Reason.CONTEST)
        .values("ref_id")
        .distinct()
        .count()
    )
    codes = {code for _, code in STREAK_MILESTONES} | {PROFILE_COMPLETE}
    done = set(
        UserQuestCompletion.objects.filter(user=user, quest__code__in=codes).values_list(
            "quest__code", flat=True
        )
    )

    rows: list[dict[str, Any]] = []
    for target in SOLVE_MILESTONES:
        rows.append(_row("solve", target, solved))
    for target, code in STREAK_MILESTONES:
        reached = target if code in done else user.streak_count
        rows.append(_row("streak", target, reached))
    for target in CONTEST_MILESTONES:
        rows.append(_row("contest", target, contests))
    rows.append(_row("profile", 1, 1 if PROFILE_COMPLETE in done else 0))
    return rows


def _row(group: str, target: int, progress: int) -> dict[str, Any]:
    return {
        "code": f"{group}-{target}",
        "group": group,
        "target": target,
        "progress": min(progress, target),
        "done": progress >= target,
    }


def purchases(user: User) -> list[dict[str, Any]]:
    from qvant.models import UserInventory

    return [
        {
            "code": row.item.code,
            "category": row.item.category,
            "title_uz": row.item.title_uz,
            "title_ru": row.item.title_ru,
            "title_en": row.item.title_en,
            "purchased_at": row.purchased_at,
            "is_equipped": row.is_equipped,
        }
        for row in UserInventory.objects.filter(user=user).select_related("item")
    ]
