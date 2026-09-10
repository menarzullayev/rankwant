from django.db import migrations, models


def backfill(apps, schema_editor):
    """Mavjud taxalluslarga skelet yozadi.

    Cheklov shundan KEYIN qo'shiladi — aks holda bo'sh maydonli o'n mingta
    qator bir-biriga to'qnashardi.

    O'lchandi (2026-09-10, preview): 10 026 foydalanuvchi, skelet
    to'qnashuvi 0, kirill harfli taxallus 0 — ya'ni cheklov mavjud
    ma'lumotni rad etmaydi.
    """
    from core.handles import skeleton

    User = apps.get_model("core", "User")
    batch = []
    for pk, username in User.objects.values_list("pk", "username").iterator(chunk_size=2000):
        batch.append(User(pk=pk, username_skeleton=skeleton(username)))
        if len(batch) >= 2000:
            User.objects.bulk_update(batch, ["username_skeleton"])
            batch = []
    if batch:
        User.objects.bulk_update(batch, ["username_skeleton"])


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0005_passwordresettoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="username_skeleton",
            field=models.CharField(blank=True, db_index=True, max_length=150),
        ),
        migrations.RunPython(backfill, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                models.F("username_skeleton"),
                condition=models.Q(("username_skeleton", ""), _negated=True),
                name="uniq_username_skeleton",
            ),
        ),
    ]
