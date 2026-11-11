"""Publish the Abramyan problems and their study plan — all together (ADR-0060 § 2.6).

    python manage.py publish_abramyan

Owner decision: nothing goes out until every problem's reference solution
is AC on the real judge (`verify_abramyan`) and its empty submission is not.
The command reads the last verification attempts and refuses otherwise.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content import plans
from judging import system_attempts
from judging.verdicts import Verdict
from problems import abramyan
from problems.management.commands.verify_abramyan import ACCOUNT, EMPTY
from problems.models import Problem

PLAN = "abramyan-masalalar"


def unverified(problems: list[Problem]) -> list[str]:
    """Problems whose last verification is missing or not green."""
    bad = []
    for problem in problems:
        reference, empty = system_attempts.last_verdicts(problem, ACCOUNT, EMPTY)
        if (
            reference != Verdict.AC
            or empty is None
            or empty in ({Verdict.AC} | system_attempts.UNFINISHED)
        ):
            bad.append(problem.slug)
    return bad


class Command(BaseCommand):
    help = "Abramyan masalalari va o'quv rejasini birga nashr qiladi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        problems = list(Problem.objects.filter(source=abramyan.SOURCE).order_by("pk"))
        if not problems:
            raise CommandError("Abramyan masalalari topilmadi")
        bad = unverified(problems)
        if bad:
            raise CommandError(f"{len(bad)} ta masala tekshiruvdan o'tmagan: {', '.join(bad[:20])}")
        if options["dry_run"]:
            self.stdout.write(f"{len(problems)} ta masala nashrga tayyor (dry-run)")
            return
        with transaction.atomic():
            for problem in problems:
                problem.is_public = True
                problem.readiness = Problem.Readiness.VALIDATED
                # `save()` keeps the hooks: no number for an unofficial problem.
                problem.save()
            plans.publish(PLAN)
        self.stdout.write(self.style.SUCCESS(f"{len(problems)} ta masala nashr qilindi"))
