"""Fills `ActivityEvent` from the rows that already exist.

The table is written when things happen, so without this it would start
empty and every feed would begin on the deploy day. Each event keeps the
time of the row it came from — `auto_now_add` stamps "now" on insert, so the
real time is written in a second pass.

Same rules as `profiles.activity`: a solve's own rating change and the daily
activity rating are not events.
"""

from typing import Any

from django.db import migrations

BATCH = 500


def backfill(apps: Any, schema_editor: Any) -> None:
    ActivityEvent = apps.get_model("profiles", "ActivityEvent")
    RatingHistory = apps.get_model("ratings", "RatingHistory")
    UserSolvedProblem = apps.get_model("ratings", "UserSolvedProblem")
    QvantTransaction = apps.get_model("qvant", "QvantTransaction")
    ContestRegistration = apps.get_model("contests", "ContestRegistration")

    if ActivityEvent.objects.exists():
        return

    rows: list[tuple[Any, Any]] = []

    for solve in UserSolvedProblem.objects.select_related("problem").iterator(chunk_size=BATCH):
        rows.append(
            (
                solve.first_ac_at,
                ActivityEvent(
                    user_id=solve.user_id,
                    kind="solved",
                    ref_type="problem",
                    ref_id=solve.problem.slug,
                    data={
                        "title": solve.problem.title,
                        "difficulty": solve.difficulty_at_solve,
                    },
                ),
            )
        )

    history = RatingHistory.objects.exclude(reason="problem_solved").exclude(
        rating_type="activity"
    )
    for row in history.iterator(chunk_size=BATCH):
        rows.append(
            (
                row.created_at,
                ActivityEvent(
                    user_id=row.user_id,
                    kind="rating",
                    ref_type=row.ref_type,
                    ref_id=row.ref_id,
                    data={
                        "type": row.rating_type,
                        "before": row.value_before,
                        "after": row.value_after,
                        "delta": row.delta,
                        "reason": row.reason,
                        "rank": row.rank,
                    },
                ),
            )
        )

    for tx in QvantTransaction.objects.iterator(chunk_size=BATCH):
        rows.append(
            (
                tx.created_at,
                ActivityEvent(
                    user_id=tx.user_id,
                    kind="qvant",
                    ref_type=tx.ref_type,
                    ref_id=tx.ref_id,
                    data={
                        "amount": tx.amount,
                        "reason": tx.reason,
                        "balance_after": tx.balance_after,
                    },
                ),
            )
        )

    registrations = ContestRegistration.objects.select_related("contest")
    for reg in registrations.iterator(chunk_size=BATCH):
        # The registration row has no timestamp of its own on older schemas.
        at = getattr(reg, "registered_at", None) or getattr(reg, "created_at", None)
        if at is None:
            continue
        rows.append(
            (
                at,
                ActivityEvent(
                    user_id=reg.user_id,
                    kind="contest",
                    ref_type="contest",
                    ref_id=reg.contest.slug,
                    data={"title": reg.contest.title},
                ),
            )
        )

    created = ActivityEvent.objects.bulk_create([event for _, event in rows], batch_size=BATCH)
    for (at, _), event in zip(rows, created, strict=True):
        event.created_at = at
    ActivityEvent.objects.bulk_update(created, ["created_at"], batch_size=BATCH)


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0007_home_dashboard"),
        ("ratings", "0002_alter_ratinghistory_reason"),
        ("qvant", "0004_hack_reason"),
        ("contests", "0006_contest_organizers"),
    ]

    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
