"""50k: pending navbat va profil urinishlari uchun indeks."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("judging", "0006_hacked_verdict"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="attempt",
            index=models.Index(fields=["verdict", "created_at"], name="attempt_pending_feed"),
        ),
        migrations.AddIndex(
            model_name="attempt",
            index=models.Index(fields=["user", "-created_at"], name="attempt_user_feed"),
        ),
    ]
