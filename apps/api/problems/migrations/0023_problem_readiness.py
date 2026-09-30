"""Readiness column — M1, add step (D8 · ADR-0037).

The column lands NULLable and WITHOUT a default: the deploy that runs this
migration still serves the previous code, which knows nothing about
`readiness`. 0024 fills every row before the NOT NULL switch, so no half
written state is ever visible to the old code.

The composite index is for the remediation dashboard — it groups the backlog
by `readiness` and visibility (`legacy_unverified` + public = 1 222 rows).
"""

from django.db import migrations, models

READINESS_CHOICES = [
    ("draft", "Qoralama"),
    ("needs_tests", "Test kerak"),
    ("has_hidden_tests", "Yashirin test bor"),
    ("checker_validated", "Checker tekshirilgan"),
    ("ref_solution_verified", "Etalon tekshirilgan"),
    ("validated", "Tasdiqlangan"),
    ("legacy_unverified", "Arxiv (tekshirilmagan)"),
    ("blocked", "Bloklangan"),
    ("needs_review", "Ko'rik kerak"),
]


class Migration(migrations.Migration):
    dependencies = [("problems", "0022_problem_authors")]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="readiness",
            field=models.CharField(
                choices=READINESS_CHOICES,
                max_length=24,
                null=True,
                db_index=True,
            ),
        ),
        migrations.AddIndex(
            model_name="problem",
            index=models.Index(fields=["readiness", "is_public"], name="problem_readiness_pub"),
        ),
    ]
