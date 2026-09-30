"""Readiness harness — proves S3 and S4 with a real judge (ADR-0037).

    python manage.py verify_readiness a-plus-b            # dry run, one problem
    python manage.py verify_readiness --apply             # every problem
    python manage.py verify_readiness --apply round-a     # write the result

Two submissions per problem, both standalone (no `Attempt` is created):

  S3  the reference solution — must be AC
  S4  a program that prints the sample answer — must NOT be AC

Outcome: `blocked` when either fails, `ref_solution_verified` when both hold.
`validated` is never written here: the last step is a staff signature.

⚠️ Run with `beat` STOPPED. `drain_results` routes an `attempt_id=0` result
with no `hack_id`/`custom_run_id` to `apply_result`, which drops it — a live
beat would swallow every probe result and every problem would look broken.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from problems.models import Problem
from problems.readiness import HarnessError, apply_verdict, verify


class Command(BaseCommand):
    help = "Runs the readiness harness (S3/S4) for problems."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "slugs",
            nargs="*",
            help="Empty = every problem (ones without a reference solution are skipped)",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the new readiness (default: dry run)",
        )
        parser.add_argument(
            "--poll-timeout",
            type=int,
            default=5,
            help="Seconds to wait for one judge result (default 5)",
        )
        parser.add_argument(
            "--rounds",
            type=int,
            default=3,
            help="How many times to poll before giving up (default 3)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        slugs: list[str] = options["slugs"]
        queryset = Problem.objects.order_by("slug")
        if slugs:
            queryset = queryset.filter(slug__in=slugs)
            missing = set(slugs) - set(queryset.values_list("slug", flat=True))
            if missing:
                raise CommandError(f"no such problem: {', '.join(sorted(missing))}")

        blocked = 0
        verified = 0
        skipped = 0
        for problem in queryset:
            try:
                target = verify(problem)
            except HarnessError as exc:
                # No answer is infrastructure, not evidence. Skipping keeps a
                # judge outage from blocking the whole bank.
                skipped += 1
                self.stdout.write(f"{problem.slug}: SKIPPED — {exc}")
                continue

            if target == problem.readiness:
                self.stdout.write(f"{problem.slug}: unchanged ({target})")
                continue
            if target == Problem.Readiness.BLOCKED:
                blocked += 1
            else:
                verified += 1
            if options["apply"]:
                apply_verdict(problem, target)
                self.stdout.write(
                    self.style.WARNING(f"{problem.slug}: {problem.readiness} -> {target} (written)")
                )
            else:
                self.stdout.write(f"{problem.slug}: {problem.readiness} -> {target} (dry run)")

        self.stdout.write(
            self.style.SUCCESS(f"blocked={blocked} verified={verified} skipped={skipped}")
        )
