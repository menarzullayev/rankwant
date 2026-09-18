"""Rebuild the stored user counters from their sources (ADR-0024).

    python manage.py recount_user_stats --check   # report only, exit 1 on drift
    python manage.py recount_user_stats           # repair

Drift appears when rows change outside the services: a cascade delete, an
import, a manual fix in the admin, or events written between the migration's
backfill and the new code going live.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from core import user_stats


class Command(BaseCommand):
    help = "Compare the stored user counters with their sources and repair them."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--check",
            action="store_true",
            help="Only report differences; exit 1 when there are any.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        check = bool(options["check"])
        diffs = user_stats.reconcile(fix=not check)
        by_field = Counter(field for _, field, _, _ in diffs)
        users = len({user_id for user_id, _, _, _ in diffs})
        if not diffs:
            self.stdout.write("user counters match their sources")
            return
        verb = "differ" if check else "repaired"
        summary = ", ".join(f"{field} {count}" for field, count in sorted(by_field.items()))
        self.stdout.write(f"{len(diffs)} values in {users} users {verb}: {summary}")
        for user_id, field, stored, wanted in diffs[:20]:
            self.stdout.write(f"  user {user_id}: {field} {stored!r} -> {wanted!r}")
        if check:
            raise CommandError("user counters drifted; run without --check to repair")
