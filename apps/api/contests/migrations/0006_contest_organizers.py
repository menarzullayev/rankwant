"""Contest.organizers M2M — ADR-0025 (qaror 23)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contests", "0005_hack_windows"),
        ("core", "0020_user_competitor_parity"),
    ]

    operations = [
        migrations.AddField(
            model_name="contest",
            name="organizers",
            field=models.ManyToManyField(
                blank=True,
                help_text="O'z kontestini draft qilib yaratadi/tahrirlaydi; nashr — staff-ops (ADR-0025)",
                related_name="organized_contests",
                to="core.user",
            ),
        ),
    ]
