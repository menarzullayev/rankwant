"""Ommaviy profil — ma'lumot, faoliyat, yutuqlar, xaridlar.

Maxfiylik qoidasi bitta joyda: `hidden_fields` dagi maydon egasidan
boshqa hech kimga ko'rinmaydi. Qolgani — standart bo'yicha ochiq
(foydalanuvchi shuni tanladi, yashirish uning o'z qo'lida).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from django.utils import timezone

from core import sessions
from core.models import User
from profiles import titles
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
#: «Chempion» nishoni g'alabadan keyin shuncha kun turadi.
CHAMPION_DAYS = 365


def build_profile(user: User, viewer: User | None) -> dict[str, Any]:
    from profiles import achievements
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
        for field in ("region", "district", "city"):
            if getattr(user, field):
                info[field] = getattr(user, field)
    if visible("school") and (user.school_ref_id or user.school):
        # Katalogdagi maktab ustun: maktab reytingi va sinfdoshlar shunga tayanadi.
        info["school"] = user.school_ref.name if user.school_ref is not None else user.school
        if user.school_ref_id:
            info["school_id"] = str(user.school_ref_id)
    for field in ("grade", "website"):
        value = getattr(user, field)
        if visible(field) and value:
            info[field] = value

    seen = sessions.last_seen(user) if visible("online") else None
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
        )
        if visible("social")
        else [],
        "followers": Follow.objects.filter(following=user).count(),
        "following": Follow.objects.filter(follower=user).count(),
        "is_following": (
            Follow.objects.filter(follower=viewer, following=user).exists()
            if viewer is not None and not owner
            else None
        ),
        "cosmetics": equipped(user),
        "title": titles.user_title(user),
        # RankWant unvonidan (yuqorida) alohida — manbadagi daraja
        # (ADR-0026). `title` hisoblanadi, bu ikkisi saqlanadi.
        "cf_title": user.rank_title or "",
        "cf_max_title": user.max_rank_title or "",
        "friend_count": user.friend_count,
        # Banner — foydalanuvchi yuklagan rasm, shuning uchun
        # `visible(...)` tekshiruvi shart (`country` bilan bir qoida).
        "title_photo_url": user.title_photo_url if visible("title_photo") else "",
        "roles": roles(user),
        "last_seen": seen,
        "online": seen is not None
        and (timezone.now() - seen).total_seconds() < sessions.ONLINE_WINDOW,
        "pinned": achievements.pinned(user),
        "coach": coaches(user) if visible("coach") else [],
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


def coaches(user: User) -> list[dict[str, Any]]:
    """Murabbiy — o'quvchi a'zo bo'lgan faol auditoriyaning egasi (ADR-0017)."""
    from classroom.models import ClassroomMember

    owners = (
        User.objects.filter(
            owned_classrooms__members__user=user,
            owned_classrooms__members__role=ClassroomMember.Role.STUDENT,
            owned_classrooms__is_active=True,
            is_active=True,
        )
        .exclude(pk=user.pk)
        .distinct()
        .order_by("username")[:3]
    )
    return [
        {
            "username": owner.username,
            "display_name": owner.display_name,
            "title": titles.user_title(owner),
        }
        for owner in owners
    ]


def roles(user: User) -> list[dict[str, str]]:
    """Profil nishonlari (ADR-0018): xodim, masala muallifi, hakam, chempion."""
    from contests.models import Contest
    from problems.models import Problem

    out: list[dict[str, str]] = []
    if user.is_staff:
        out.append({"code": "staff"})
    if Problem.objects.filter(author=user, is_public=True).exists():
        out.append({"code": "author"})
    if Contest.objects.filter(jury=user).exists():
        out.append({"code": "jury"})
    won = champion_of(user)
    if won is not None:
        out.append({"code": "champion", "contest": won.slug, "contest_title": won.title})
    return out


def champion_of(user: User) -> Any:
    """Oxirgi 365 kunda reytingli musobaqada birinchi natija — virtual emas.

    `Standing.rank` ketma-ket raqam: birinchi bilan TENG natija ham g'olib.
    Hech narsa yechmagan «birinchi» chempion emas.
    """
    from contests.models import Contest, ContestRegistration, Standing

    now = timezone.now()
    virtual = ContestRegistration.objects.filter(user=user, virtual_start_at__isnull=False).values(
        "contest_id"
    )
    rows = (
        Standing.objects.filter(
            user=user,
            contest__is_rated=True,
            contest__is_public=True,
            contest__is_virtual=False,
            contest__end_at__gte=now - timedelta(days=CHAMPION_DAYS),
            contest__end_at__lte=now,
        )
        .exclude(contest_id__in=virtual)
        .select_related("contest")
        .order_by("-contest__end_at")
    )
    for row in rows:
        top = Standing.objects.filter(contest_id=row.contest_id, rank=1).first()
        if top is None:
            continue
        ioi = row.contest.scoring_type == Contest.Scoring.IOI
        mine = (row.total_score,) if ioi else (row.solved_count, row.penalty)
        best = (top.total_score,) if ioi else (top.solved_count, top.penalty)
        if mine == best and mine[0] > 0:
            return row.contest
    return None


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
