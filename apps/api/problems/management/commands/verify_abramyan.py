"""Check the Abramyan import on the real judge (ADR-0060 § 2.6).

    python manage.py verify_abramyan --report /tmp/abramyan-verify.json
    python manage.py verify_abramyan --codes Begin1,File1 --wait 600

Each problem gets two submissions from one system account, through the
path users take (attempt → queue → judge → result): the reference solution,
which must be AC, and an empty program, which must not be — a test set that
accepts no output proves nothing. Owner decision (round 4): it runs on the
production judge now, and its attempts stay until the owner decides on them.
"""

from __future__ import annotations

import json
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from core.models import User
from judging import system_attempts
from judging.verdicts import Verdict
from problems import abramyan
from problems.models import Problem, ReferenceSolution

ACCOUNT = "abramyan-verify"
EMPTY = "pass\n"


class Command(BaseCommand):
    help = "Abramyan masalalarining namuna yechimlarini haqiqiy judge'da tekshiradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--codes", default="", help="Vergul bilan: Begin1,File1")
        parser.add_argument("--wait", type=int, default=7200, help="Kutish chegarasi, soniya")
        parser.add_argument("--report", default="", help="JSON hisobot yo'li")

    def handle(self, *args: Any, **options: Any) -> None:
        problems = Problem.objects.filter(source=abramyan.SOURCE).order_by("pk")
        wanted = {abramyan.slug(c.strip()) for c in options["codes"].split(",") if c.strip()}
        if wanted:
            problems = problems.filter(slug__in=wanted)
        if not problems.exists():
            raise CommandError("Abramyan masalalari topilmadi — avval import_abramyan")
        account, _ = User.objects.get_or_create(
            username=ACCOUNT, defaults={"is_active": False, "email": ""}
        )

        sent: list[tuple[Problem, int, str]] = []
        for problem in problems:
            reference = ReferenceSolution.objects.filter(problem=problem).first()
            if reference is None:
                self.stderr.write(f"{problem.slug}: namuna yechim yo'q")
                continue
            for kind, source, language in (
                ("reference", reference.source, reference.language),
                ("empty", EMPTY, reference.language),
            ):
                sent.append(
                    (problem, system_attempts.submit(account, problem, language, source), kind)
                )
        self.stdout.write(f"{len(sent)} ta yuborish navbatga qo'yildi")

        deadline = time.monotonic() + options["wait"]
        pending = {attempt for _, attempt, _ in sent}
        while pending and time.monotonic() < deadline:
            done = system_attempts.finished(pending)
            pending -= done
            self.stdout.write(f"  kutilmoqda: {len(pending)} / {len(sent)}")
            if pending:
                time.sleep(15)

        rows = []
        failures = 0
        verdicts = system_attempts.results([attempt for _, attempt, _ in sent])
        for problem, attempt, kind in sent:
            judged = verdicts[attempt]
            ok = (
                judged["verdict"] == Verdict.AC
                if kind == "reference"
                else judged["verdict"] not in ({Verdict.AC} | system_attempts.UNFINISHED)
            )
            failures += not ok
            rows.append(
                {
                    "slug": problem.slug,
                    "kind": kind,
                    "verdict": judged["verdict"],
                    "ok": ok,
                    "attempt": judged["pk"],
                    "failed_test": judged["failed_test_index"],
                    "time_ms": judged["time_ms"],
                    "memory_kb": judged["memory_kb"],
                }
            )
        summary = {
            "problems": problems.count(),
            "submissions": len(rows),
            "failures": failures,
            "still_pending": len(pending),
        }
        if options["report"]:
            Path(options["report"]).write_text(
                json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1),
                encoding="utf-8",
            )
        for row in rows:
            if not row["ok"]:
                self.stdout.write(
                    f"  ✗ {row['slug']} {row['kind']}: {row['verdict']} (test {row['failed_test']})"
                )
        style = self.style.SUCCESS if failures == 0 and not pending else self.style.ERROR
        self.stdout.write(style(json.dumps(summary)))
        if failures or pending:
            raise CommandError("tekshiruv yashil emas")
