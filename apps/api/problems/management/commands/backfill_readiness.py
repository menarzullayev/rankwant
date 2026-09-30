"""Readiness backfill audit — the M1 numbers without running the migration.

The migration (`0024_backfill_readiness`) already writes the same three
groups. This command exists because the numbers are an acceptance criterion
(WP1 ③): it prints them on the live database BEFORE deploy and verifies them
AFTER it, without judging anything.

    python manage.py backfill_readiness            # audit only (dry run)
    python manage.py backfill_readiness --apply    # write the same groups

Groups (static conditions only — the judge is never called):

    A  public, no hidden test  -> `legacy_unverified`
    B  public, hidden test     -> `needs_review`
    C  the rest                -> `draft`
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from problems.models import Problem
from problems.readiness import Readiness


class Command(BaseCommand):
    help = "Readiness backfill audit (M1): A/B/C counts and the remaining NULL rows."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the groups (default: dry run, print only)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        public = Problem.objects.filter(is_public=True).annotate(
            hidden=Count("tests", filter=Q(tests__is_sample=False))
        )
        legacy_ids = list(public.filter(hidden=0).values_list("pk", flat=True))
        review_ids = list(public.filter(hidden__gt=0).values_list("pk", flat=True))
        total = Problem.objects.count()
        already = Problem.objects.filter(readiness__isnull=False).count()

        self.stdout.write(
            f"problems={total} public={len(legacy_ids) + len(review_ids)} already_set={already}"
        )
        self.stdout.write(f"A legacy_unverified={len(legacy_ids)}")
        self.stdout.write(f"B needs_review={len(review_ids)}")
        group_c = total - len(legacy_ids) - len(review_ids)
        self.stdout.write(f"C draft={group_c}")

        if not options["apply"]:
            self.stdout.write("dry run — nothing written (--apply to write)")
            return

        a = Problem.objects.filter(pk__in=legacy_ids).update(readiness=Readiness.LEGACY_UNVERIFIED)
        b = Problem.objects.filter(pk__in=review_ids).update(readiness=Readiness.NEEDS_REVIEW)
        c = Problem.objects.filter(readiness__isnull=True).update(readiness=Readiness.DRAFT)
        left = Problem.objects.filter(readiness__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f"written: A={a} B={b} C={c} null_left={left}"))
        if left:
            self.stderr.write(self.style.ERROR(f"{left} row(s) still NULL"))
            raise SystemExit(1)
