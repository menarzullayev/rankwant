"""Adds the quests already finished to `ActivityEvent`.

The profile feed now reads this table instead of `UserQuestCompletion`;
without the rows a profile would lose the quests finished before this
deploy. Each event keeps the time the quest was completed.
"""

from typing import Any

from django.db import migrations

BATCH = 500


def backfill(apps: Any, schema_editor: Any) -> None:
    ActivityEvent = apps.get_model("profiles", "ActivityEvent")
    UserQuestCompletion = apps.get_model("qvant", "UserQuestCompletion")

    if ActivityEvent.objects.filter(kind="quest").exists():
        return

    rows = []
    done = UserQuestCompletion.objects.select_related("quest")
    for row in done.iterator(chunk_size=BATCH):
        rows.append(
            (
                row.completed_at,
                ActivityEvent(
                    user_id=row.user_id,
                    kind="quest",
                    ref_type="quest",
                    ref_id=row.quest.code,
                    data={
                        "title_uz": row.quest.title_uz,
                        "title_ru": row.quest.title_ru,
                        "title_en": row.quest.title_en,
                        "awarded": row.awarded,
                    },
                ),
            )
        )

    created = ActivityEvent.objects.bulk_create([event for _, event in rows], batch_size=BATCH)
    for (at, _), event in zip(rows, created, strict=True):
        event.created_at = at
    ActivityEvent.objects.bulk_update(created, ["created_at"], batch_size=BATCH)


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0009_activity_quest_kind"),
        ("qvant", "0004_hack_reason"),
    ]

    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
