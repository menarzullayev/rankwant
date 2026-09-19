"""Staff guruhlari seed — ADR-0025 (qaror 23).

3 guruh yaratiladi va MAVJUD barcha `is_staff` foydalanuvchilar uchalarga ham
qo'shiladi — ya'ni joriy xodim hech qanday huquqini yo'qotmaydi. Guruhlarning
model permission'lari bu yerda BIRIKTIRILMAYDI: `auth_permission` qatorlari
post_migrate to'laganidan keyin paydo bo'ladi — ularni `core/groups.py`
dagi `sync_staff_groups()` post_migrate receiver'i biriktiradi.
"""

from __future__ import annotations

from django.db import migrations


GROUPS: tuple[str, ...] = ("staff-support", "staff-content", "staff-ops")


def seed_groups(apps, schema_editor) -> None:
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("core", "User")

    created = []
    for name in GROUPS:
        group, _ = Group.objects.get_or_create(name=name)
        created.append(group)

    # Joriy xodim hech narsani yo'qotmasin: mavjud barcha `is_staff`
    # uchala guruhga ham qo'shiladi (superuser allaqachon bypass).
    for user in User.objects.filter(is_staff=True).iterator():
        user.groups.add(*created)


def unseed_groups(apps, schema_editor) -> None:
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUPS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_user_competitor_parity"),
    ]

    operations = [
        migrations.RunPython(seed_groups, unseed_groups),
    ]
