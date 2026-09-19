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

#: Personal data that `anonymize` clears and `export` returns. Every `User`
#: field is listed here or in `KEPT_FIELDS`, and `tests/test_account_fields.py`
#: fails on a field in neither. A new personal column therefore cannot slip past
#: account deletion, as `phone` did until 2026-09-18.
CLEARED_FIELDS: tuple[str, ...] = (
    "password",
    "is_active",
    "username",
    "username_skeleton",
    "display_name",
    "first_name",
    "last_name",
    "email",
    "email_verified_at",
    "avatar_url",
    "bio",
    "telegram_id",
    "country",
    "region",
    "district",
    "city",
    "school",
    "school_ref",
    "grade",
    "website",
    "birth_date",
    "phone",
    "hidden_fields",
    "pinned_achievements",
    "ui_prefs",
    "notify_prefs",
    "marketing_opt_in",
    "shirt_size",
    "postal_recipient",
    "postal_country",
    "postal_region",
    "postal_city",
    "postal_address",
    "postal_code",
    "coach_can_view_attempts",
    "message_min_rating",
    "device_fingerprint",
    "duel_ready_until",
    "last_seen_at",
    # ADR-0026: a profile banner is uploaded content, like `avatar_url`.
    "title_photo_url",
)

#: Kept on purpose. Results and counters stay, as the module docstring explains;
#: `terms_accepted_at` records what the person agreed to, and the plan fields
#: are a billing record.
KEPT_FIELDS: tuple[str, ...] = (
    "id",
    "last_login",
    "is_superuser",
    "is_staff",
    "date_joined",
    "groups",
    "user_permissions",
    "username_changed_at",
    "locale",
    "theme",
    "rating_skills",
    "rating_contest",
    "rating_activity",
    "rating_challenges",
    "rated_contest_count",
    "max_rating_skills",
    "max_rating_contest",
    "max_rating_activity",
    "max_rating_challenges",
    "solved_count",
    "streak_count",
    "streak_max",
    "streak_freeze_until",
    "last_active_date",
    "terms_accepted_at",
    "plan",
    "plan_expires_at",
    "contribution",
    # ADR-0026: rating metadata, kept for the same reason as `rating_contest`.
    "rank_title",
    "max_rank_title",
    "friend_count",
)


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
    # Eski taxalluslar SAQLANADI, faqat egasidan uziladi.
    #
    # Ilgari bu yerda `.delete()` edi — `usernames.reserved()` aynan shu
    # jadvaldan o'qiydi, ya'ni 90 kunlik bandlik himoyasi ishlamasdi:
    # odam hisobini o'chirib, taxallusini DARHOL qayta olib, eski
    # egasining obro'si bilan standings'da turardi (o'lchandi).
    # `user=None` — ikkala maqsad ham bajariladi: `reserved()` ishlaydi,
    # lekin qator endi anonimlashtirilgan odamga ishora qilmaydi.
    UsernameHistory.objects.filter(user=user).update(user=None)
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
    user.district = ""
    user.city = ""
    user.school_ref = None
    user.school = ""
    user.grade = ""
    user.website = ""
    user.birth_date = None
    user.phone = ""
    user.email_verified_at = None
    user.hidden_fields = []
    user.pinned_achievements = []
    user.ui_prefs = {}
    user.notify_prefs = {}
    user.marketing_opt_in = False
    user.shirt_size = ""
    user.postal_recipient = ""
    user.postal_country = ""
    user.postal_region = ""
    user.postal_city = ""
    user.postal_address = ""
    user.postal_code = ""
    user.coach_can_view_attempts = False
    user.message_min_rating = None
    user.device_fingerprint = ""
    user.duel_ready_until = None
    user.last_seen_at = None
    # ADR-0026: the banner is uploaded content, so it is cleared and its
    # stored file removed, exactly like the avatar above.
    old_title_photo = avatars.name_from_url(user.title_photo_url)
    user.title_photo_url = ""
    user.is_active = False
    # Sessiya paroldan olingan hashga bog'langan — parolni yaroqsiz
    # qilish ochiq qolgan barcha sessiyalarni ham uzadi.
    user.set_unusable_password()
    user.save()
    if old_avatar:
        avatars.delete(old_avatar)
    if old_title_photo:
        avatars.delete(old_title_photo)


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
            "email_verified_at": user.email_verified_at,
            "display_name": user.display_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "telegram_id": user.telegram_id,
            "locale": user.locale,
            "theme": user.theme,
            "country": user.country,
            "region": user.region,
            "district": user.district,
            "city": user.city,
            "school": user.school,
            "school_ref": user.school_ref.name if user.school_ref is not None else None,
            "grade": user.grade,
            "website": user.website,
            "birth_date": user.birth_date,
            "phone": user.phone,
            "shirt_size": user.shirt_size,
            "postal_recipient": user.postal_recipient,
            "postal_country": user.postal_country,
            "postal_region": user.postal_region,
            "postal_city": user.postal_city,
            "postal_address": user.postal_address,
            "postal_code": user.postal_code,
            "coach_can_view_attempts": user.coach_can_view_attempts,
            "message_min_rating": user.message_min_rating,
            "device_fingerprint": user.device_fingerprint,
            "duel_ready_until": user.duel_ready_until,
            "hidden_fields": user.hidden_fields,
            "pinned_achievements": user.pinned_achievements,
            "ui_prefs": user.ui_prefs,
            "notify_prefs": user.notify_prefs,
            "marketing_opt_in": user.marketing_opt_in,
            "terms_accepted_at": user.terms_accepted_at,
            "date_joined": user.date_joined,
            "last_seen_at": user.last_seen_at,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at,
            "rating_skills": user.rating_skills,
            "rating_contest": user.rating_contest,
            "rating_activity": user.rating_activity,
            "rating_challenges": user.rating_challenges,
            "max_rating_skills": user.max_rating_skills,
            "max_rating_contest": user.max_rating_contest,
            "max_rating_activity": user.max_rating_activity,
            "max_rating_challenges": user.max_rating_challenges,
            "solved_count": user.solved_count,
            "streak_count": user.streak_count,
            "streak_max": user.streak_max,
            "contribution": user.contribution,
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
