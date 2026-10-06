"""Installs the reference problems — one for each way of grading.

    python manage.py seed_reference_problems              # install and publish
    python manage.py seed_reference_problems --draft      # install, keep private

`special`, `interactive` and `scorer` each get a small deterministic problem
(`problems/reference_problems.py`). The command is idempotent: it refreshes
the statement, the tests, the checker and the reference solution in place.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from problems.reference_problems import install


class Command(BaseCommand):
    help = "Installs the special-checker, interactive and scorer reference problems."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--draft",
            action="store_true",
            help="Leave the problems private (default: publish them)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        for problem in install(publish=not options["draft"]):
            state = "public" if problem.is_public else "draft"
            self.stdout.write(
                f"{problem.slug}: {problem.checker_type}, {problem.tests.count()} tests, {state}"
            )
