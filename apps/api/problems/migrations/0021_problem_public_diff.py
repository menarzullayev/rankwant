"""50k: arxiv filtri (is_public + difficulty) uchun kompozit indeks."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0020_judge_languages_group3"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="problem",
            index=models.Index(fields=["is_public", "difficulty"], name="problem_public_diff"),
        ),
    ]
