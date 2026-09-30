"""Readiness backfill — M1, backfill + switch step (D8 · D8-F).

Three groups, decided by static conditions only. The judge is NOT called:
S3/S4 need a sandbox, so nothing can be `validated` after this migration —
remediation is later work.

  A  public and no hidden test  -> `legacy_unverified`  (1 222 expected)
  B  public and a hidden test   -> `needs_review`       (~4 expected)
  C  everything else            -> `draft`

D8-F: `is_public` is NOT touched. Group A stays readable — it only loses the
right to enter a graded contest.

Criterion ③ of WP1 is `SELECT count(*) WHERE is_public AND readiness IS NULL`
= 0; the audit numbers are printed by the migration itself.
"""

from django.db import migrations, models
from django.db.models import Count, Q

#: Mirrors `Problem.Readiness` — a data migration must not import the model,
#: it works on the historical state.
LEGACY_UNVERIFIED = "legacy_unverified"
NEEDS_REVIEW = "needs_review"
DRAFT = "draft"

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


def backfill(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
    """Writes the three groups and prints the audit numbers."""
    Problem = apps.get_model("problems", "Problem")
    public = Problem.objects.filter(is_public=True).annotate(
        hidden=Count("tests", filter=Q(tests__is_sample=False))
    )
    # `.update()` refuses an annotated queryset, so the ids are materialised
    # first — 1 222 ids is nothing next to a per-row save().
    legacy_ids = list(public.filter(hidden=0).values_list("pk", flat=True))
    review_ids = list(public.filter(hidden__gt=0).values_list("pk", flat=True))

    group_a = Problem.objects.filter(pk__in=legacy_ids).update(readiness=LEGACY_UNVERIFIED)
    group_b = Problem.objects.filter(pk__in=review_ids).update(readiness=NEEDS_REVIEW)
    group_c = Problem.objects.filter(readiness__isnull=True).update(readiness=DRAFT)
    left_null = Problem.objects.filter(readiness__isnull=True).count()

    print(
        f"readiness backfill (M1): A legacy_unverified={group_a} "
        f"B needs_review={group_b} C draft={group_c} null_left={left_null}"
    )
    if left_null:
        raise RuntimeError(f"readiness backfill left {left_null} NULL row(s)")


class Migration(migrations.Migration):
    dependencies = [("problems", "0023_problem_readiness")]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop, elidable=True),
        migrations.AlterField(
            model_name="problem",
            name="readiness",
            field=models.CharField(
                choices=READINESS_CHOICES,
                default=DRAFT,
                max_length=24,
                db_index=True,
            ),
        ),
    ]
