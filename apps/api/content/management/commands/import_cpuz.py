"""`manage.py import_cpuz` — load the vendored cp.uz library (ADR-0062).

Safe to run again: it changes only what changed and never overwrites an
article edited here. Without `--publish` nothing becomes public; with it,
every reviewed article is published at once and the others are listed.
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from content.cpuz import import_library


class Command(BaseCommand):
    help = "Import the vendored cp.uz algorithms library (ADR-0062)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--publish",
            action="store_true",
            help="publish every reviewed article (the library goes out together)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            report = import_library(publish=options["publish"])
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            f"created {len(report.created)}, updated {len(report.updated)}, "
            f"unchanged {len(report.unchanged)}, kept (edited here) {len(report.kept_edited)}"
        )
        for ref in report.kept_edited:
            self.stdout.write(f"  kept: {ref}")
        if options["publish"]:
            self.stdout.write(
                f"published {len(report.published)}, not published {len(report.not_published)}"
            )
            for ref in report.not_published:
                self.stdout.write(f"  not reviewed: {ref}")
