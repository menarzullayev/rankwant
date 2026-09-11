"""Tarixiy yutuqlarni tiklaydi — Qvant'siz (`awarded=0`), ADR-0018.

Qvant faqat shu kundan keyingi YANGI yutuq uchun. Sana iloji boricha
haqiqiy: N-masala — N-yechimning birinchi AC vaqti, N-musobaqa — N-reytingli
musobaqa hisoblangan vaqt, streak va profil — quest bajarilgan vaqt.
"""

from typing import Any

from django.db import migrations
from django.db.models import F, Min, Window
from django.db.models.functions import RowNumber
from django.utils import timezone

SOLVE = (1, 10, 100, 500, 1000)
CONTEST = (1, 10, 50)
QUESTS = {
    "streak_7": "streak-7",
    "streak_30": "streak-30",
    "streak_365": "streak-365",
    "profile_complete": "profile-1",
}


def backfill(apps: Any, schema_editor: Any) -> None:
    UserAchievement = apps.get_model("profiles", "UserAchievement")
    UserSolvedProblem = apps.get_model("ratings", "UserSolvedProblem")
    Standing = apps.get_model("contests", "Standing")
    UserQuestCompletion = apps.get_model("qvant", "UserQuestCompletion")
    User = apps.get_model("core", "User")

    def nth(queryset: Any, order: str) -> Any:
        return queryset.annotate(
            n=Window(
                RowNumber(), partition_by=[F("user_id")], order_by=[F(order).asc(), F("id").asc()]
            )
        )

    rows = [
        UserAchievement(user_id=user_id, code=f"solve-{n}", achieved_at=at)
        for user_id, n, at in nth(UserSolvedProblem.objects.all(), "first_ac_at")
        .filter(n__in=SOLVE)
        .values_list("user_id", "n", "first_ac_at")
    ]

    # Sanoq — `rated_contest_count` (profil ham shuni ko'rsatadi). Kichik
    # musobaqa reytingsiz yakunlanadi, lekin `ratings_applied_at` oladi —
    # shuning uchun standings faqat SANANI beradi, sanoqni emas.
    when = {
        (user_id, n): at
        for user_id, n, at in nth(
            Standing.objects.filter(
                contest__is_rated=True, contest__ratings_applied_at__isnull=False
            ),
            "contest__ratings_applied_at",
        )
        .filter(n__in=CONTEST)
        .values_list("user_id", "n", "contest__ratings_applied_at")
    }
    now = timezone.now()
    for user_id, count in User.objects.filter(rated_contest_count__gt=0).values_list(
        "id", "rated_contest_count"
    ):
        rows += [
            UserAchievement(
                user_id=user_id, code=f"contest-{n}", achieved_at=when.get((user_id, n), now)
            )
            for n in CONTEST
            if count >= n
        ]

    rows += [
        UserAchievement(
            user_id=row["user_id"], code=QUESTS[row["quest__code"]], achieved_at=row["at"]
        )
        for row in UserQuestCompletion.objects.filter(quest__code__in=QUESTS)
        .values("user_id", "quest__code")
        .annotate(at=Min("completed_at"))
    ]
    UserAchievement.objects.bulk_create(rows, batch_size=1000, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0003_userachievement"),
        ("core", "0011_user_pinned_achievements"),
        ("contests", "0003_contest_jury"),
        ("qvant", "0003_alter_qvanttransaction_reason"),
        ("ratings", "0002_alter_ratinghistory_reason"),
    ]

    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
