"""Hisobni o'chirish va shaxsiy ma'lumot eksporti.

«O'chirish» — ANONIMLASHTIRISH. Tugagan musobaqa jadvalidan qatnashchini
butunlay olib tashlash qolganlarning o'rnini siljitadi, masalaning
yechuvchilar sanog'ini buzadi va duel tarixida bo'shliq qoldiradi — ya'ni
boshqalarning natijasini o'zgartiradi. Shuning uchun yechim, reyting va
jadval yozuvlari JOYIDA qoladi, ularni odamga bog'lab turgan ma'lumot esa
o'chadi.

Nom `neytrino_` — `neytron_` (stress sinovi foydalanuvchilari) bilan bir
oiladan. Neytrino zaryadsiz va deyarli hech narsa bilan ta'sirlashmaydi:
izi bor, o'zi yo'q.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import Q

from core.models import ApiToken, User

#: `neytron_` (stress sinovi) bilan to'qnashmaydi: `startswith` boshqa.
PREFIX = "neytrino"


def anonymous_name(user: User) -> str:
    return f"{PREFIX}_{user.pk:05d}"


@transaction.atomic
def anonymize(user: User) -> None:
    """Shaxsiy ma'lumotni o'chiradi, natijalarni qoldiradi."""
    from judging.models import CustomRun
    from notifications.models import Notification
    from problems.models import Favourite

    # Ommaviy yozuvda o'rni yo'q, faqat shaxsiy: xabarnomalar, shaxsiy
    # sinov ishga tushirishlari (ichida foydalanuvchi kodi bor),
    # sevimlilar va tokenlar (nomi odam qo'ygan matn).
    Notification.objects.filter(user=user).delete()
    CustomRun.objects.filter(user=user).delete()
    Favourite.objects.filter(user=user).delete()
    ApiToken.objects.filter(user=user).delete()

    from core import avatars
    from core.models import SocialAccount, UsernameHistory, UserSession
    from profiles import teams
    from profiles.models import (
        Education,
        ExternalProfile,
        Follow,
        UserSkill,
        UserTechnology,
        WorkExperience,
    )

    # Profilning ro'yxat qismlari — hammasi shaxsiy ma'lumot.
    for model in (UserSkill, UserTechnology, Education, WorkExperience, ExternalProfile):
        model.objects.filter(user=user).delete()
    Follow.objects.filter(Q(follower=user) | Q(following=user)).delete()
    # Jamoa yo'qolmaydi: egalik qolgan a'zolarga o'tadi.
    teams.leave_all(user)
    # Provayder bog'lanishi o'chmasa, o'sha Google/Telegram bilan qayta
    # kelgan odam yangi hisob ocha olmasdi — `uniq_social_uid` band qolardi.
    SocialAccount.objects.filter(user=user).delete()
    # Eski taxalluslar odamni yangi nomiga bog'lab turadi.
    UsernameHistory.objects.filter(user=user).delete()
    UserSession.objects.filter(user=user).delete()
    old_avatar = avatars.name_from_url(user.avatar_url)

    user.username = anonymous_name(user)
    user.display_name = f"Neytrino {user.pk}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""
    user.bio = ""
    user.avatar_url = ""
    user.telegram_id = None
    user.country = ""
    user.region = ""
    user.school = ""
    user.grade = ""
    user.website = ""
    user.birth_date = None
    user.hidden_fields = []
    user.ui_prefs = {}
    user.notify_prefs = {}
    user.is_active = False
    # Sessiya paroldan olingan hashga bog'langan — parolni yaroqsiz
    # qilish ochiq qolgan barcha sessiyalarni ham uzadi.
    user.set_unusable_password()
    user.save()
    if old_avatar:
        avatars.delete(old_avatar)


def is_anonymized(user: User) -> bool:
    return user.username.startswith(f"{PREFIX}_")


def export(user: User) -> dict[str, Any]:
    """Foydalanuvchining o'z ma'lumoti — o'chirishdan oldin olib qolish uchun."""
    from contests.models import ContestRegistration, Standing
    from duels.models import Duel
    from judging.models import Attempt
    from quizzes.models import QuizAttempt
    from qvant.models import QvantTransaction, UserInventory
    from ratings.models import RatingHistory, UserSolvedProblem

    return {
        "profile": {
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "locale": user.locale,
            "theme": user.theme,
            "country": user.country,
            "region": user.region,
            "school": user.school,
            "grade": user.grade,
            "website": user.website,
            "birth_date": user.birth_date,
            "hidden_fields": user.hidden_fields,
            "ui_prefs": user.ui_prefs,
            "notify_prefs": user.notify_prefs,
            "date_joined": user.date_joined,
            "rating_skills": user.rating_skills,
            "rating_contest": user.rating_contest,
            "rating_activity": user.rating_activity,
            "rating_challenges": user.rating_challenges,
            "streak_count": user.streak_count,
        },
        "attempts": list(
            Attempt.objects.filter(user=user)
            .order_by("id")
            .values(
                "id",
                "problem__slug",
                "contest__slug",
                "language",
                "source_code",
                "verdict",
                "score",
                "time_ms",
                "memory_kb",
                "created_at",
            )
        ),
        "solved": list(
            UserSolvedProblem.objects.filter(user=user)
            .order_by("id")
            .values("problem__slug", "first_ac_at", "difficulty_at_solve")
        ),
        "rating_history": list(
            RatingHistory.objects.filter(user=user)
            .order_by("id")
            .values(
                "rating_type",
                "value_before",
                "value_after",
                "delta",
                "reason",
                "ref_type",
                "ref_id",
                "seed",
                "rank",
                "created_at",
            )
        ),
        "qvant": list(
            QvantTransaction.objects.filter(user=user)
            .order_by("id")
            .values("amount", "reason", "ref_type", "ref_id", "balance_after", "created_at")
        ),
        "inventory": list(
            UserInventory.objects.filter(user=user)
            .order_by("id")
            .values("item__code", "purchased_at", "is_equipped")
        ),
        "contests": list(
            ContestRegistration.objects.filter(user=user)
            .order_by("id")
            .values("contest__slug", "registered_at", "virtual_start_at")
        ),
        "standings": list(
            Standing.objects.filter(user=user)
            .order_by("id")
            .values("contest__slug", "rank", "solved_count", "penalty", "total_score")
        ),
        "duels": list(
            Duel.objects.filter(Q(challenger=user) | Q(opponent=user))
            .order_by("id")
            .values(
                "slug",
                "challenger__username",
                "opponent__username",
                "status",
                "challenger_solved",
                "opponent_solved",
                "is_draw",
                "created_at",
            )
        ),
        "quizzes": list(
            QuizAttempt.objects.filter(user=user)
            .order_by("id")
            .values("quiz__slug", "score", "total", "qvant_awarded", "created_at")
        ),
        **_profile_export(user),
    }


def _profile_export(user: User) -> dict[str, Any]:
    """Profil bo'limlari — ko'nikma, karyera, obuna, jamoa, kirishlar."""
    from core.models import SocialAccount, UsernameHistory, UserSession
    from profiles.models import (
        Education,
        ExternalProfile,
        Follow,
        TeamMember,
        UserSkill,
        UserTechnology,
        WorkExperience,
    )

    return {
        "skills": list(
            UserSkill.objects.filter(user=user).order_by("order").values("skill__slug", "level")
        ),
        "technologies": list(
            UserTechnology.objects.filter(user=user)
            .order_by("order")
            .values_list("slug", flat=True)
        ),
        "educations": list(
            Education.objects.filter(user=user)
            .order_by("order")
            .values("organization", "degree", "start_year", "end_year")
        ),
        "work": list(
            WorkExperience.objects.filter(user=user)
            .order_by("order")
            .values("company", "title", "start_year", "end_year")
        ),
        "external_profiles": list(
            ExternalProfile.objects.filter(user=user).values("kind", "handle")
        ),
        "following": list(
            Follow.objects.filter(follower=user).values_list("following__username", flat=True)
        ),
        "followers": list(
            Follow.objects.filter(following=user).values_list("follower__username", flat=True)
        ),
        "teams": list(
            TeamMember.objects.filter(user=user).values("team__name", "role", "joined_at")
        ),
        "social_accounts": list(
            SocialAccount.objects.filter(user=user).values("provider", "email", "created_at")
        ),
        "username_history": list(
            UsernameHistory.objects.filter(user=user).values("old_username", "changed_at")
        ),
        "sessions": list(
            UserSession.objects.filter(user=user).values(
                "user_agent", "ip", "created_at", "last_seen"
            )
        ),
    }
