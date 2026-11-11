"""`manage.py import_olympiads --source <content dir> --commit <sha>` (ADR-0062 § 2.6).

`--source` is cp.uz's `content/` at the pinned commit, prepared on the host
(the archive is not kept in this repository: it holds personal data and
unlicensed statements). Safe to run again.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from olympiads.importer import import_archive


class Command(BaseCommand):
    help = "Import the cp.uz olympiad archive from a content directory."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--source", required=True, help="cp.uz content/ directory")
        parser.add_argument("--commit", required=True, help="the cp.uz commit it was taken from")

    def handle(self, *args: Any, **options: Any) -> None:
        root = Path(options["source"])
        if not (root / "seasons").is_dir():
            raise CommandError(f"{root} has no seasons/ directory")
        report = import_archive(root, options["commit"])
        self.stdout.write(
            f"seasons {report.seasons}, events {report.events}, participants "
            f"{report.participants}, results {report.results}, tasks {report.tasks}, "
            f"kept removed {len(report.kept_removed)}"
        )
        for line in report.missing:
            self.stdout.write(f"  missing: {line}")
