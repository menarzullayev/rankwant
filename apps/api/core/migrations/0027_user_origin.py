# WP3: User.origin — foydalanuvchi kelib chiqishi (North Star metrikalar).
# ⚠️ 0027 raqami ataylab: origin/main'da 0026 `0026_client_log` bilan band
# (lokal WP3 commit'i eski tarixdan 0026 ni olgandi — merge'da graf
# vilqalanardi; QA 2026-09-29 da o'lchandi va raqamlar ko'chirildi).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_alter_user_rating_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="origin",
            field=models.CharField(
                max_length=16,
                choices=[
                    ("real", "Real"),
                    ("demo", "Demo"),
                    ("imported", "Imported"),
                    ("staff", "Staff"),
                ],
                default="real",
            ),
        ),
    ]
