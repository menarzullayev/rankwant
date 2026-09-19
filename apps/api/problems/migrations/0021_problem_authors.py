"""Problem.authors M2M — ADR-0025 (qaror 23)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0020_judge_languages_group3"),
        ("core", "0020_user_competitor_parity"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="authors",
            field=models.ManyToManyField(
                blank=True,
                help_text="O'z draft masalasini boshqaradi; nashr — staff-ops (ADR-0025)",
                related_name="authored_problems",
                to="core.user",
            ),
        ),
    ]
