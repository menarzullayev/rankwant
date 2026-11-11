"""Import the Abramyan "Programming Taskbook" package (ADR-0060 § 2.5).

    python manage.py import_abramyan --package /path/to/package --author admin
    python manage.py import_abramyan --package … --codes Begin1,File1   # a few
    python manage.py import_abramyan --package … --no-storage           # no S3

Problems land as unofficial drafts, the study plan unpublished. Running it
again updates in place: the book code is the slug, a test is its order, a
translation its language. Nothing is published here: `publish_abramyan`
does that once the verification is green (owner decision: all together).
"""

from __future__ import annotations

import json
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content import plans
from core.models import User
from problems import abramyan, storage
from problems.models import (
    Language,
    Problem,
    ProblemSolution,
    ProblemTranslation,
    ReferenceSolution,
    SolutionRole,
    TestCase,
    Topic,
)

#: The reference solutions are Python 3.
SOLUTION_LANGUAGE = "py313"
FIELDS = {"legend": "statement", "input": "input_format", "output": "output_format", "note": "note"}
_IMAGE = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)\)")


class Command(BaseCommand):
    help = "Abramyan masalalarini norasmiy qoralama sifatida import qiladi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--package", required=True, help="manifest.json turgan papka")
        parser.add_argument("--author", default="", help="Masala muallifi (foydalanuvchi nomi)")
        parser.add_argument("--codes", default="", help="Vergul bilan: Begin1,File1")
        parser.add_argument("--no-storage", action="store_true", help="Testlarni S3 ga yozmaydi")
        parser.add_argument(
            "--no-images", action="store_true", help="Shartdagi rasmni o'z omborimizga ko'chirmaydi"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        root = Path(options["package"])
        manifest_path = root / "manifest.json"
        if not manifest_path.is_file():
            raise CommandError(f"{manifest_path} topilmadi")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.root = root
        self.storage = not options["no_storage"]
        self.images = not options["no_images"]
        self.author = None
        if options["author"]:
            self.author = User.objects.filter(username=options["author"]).first()
            if self.author is None:
                raise CommandError(f"foydalanuvchi topilmadi: {options['author']}")
        language = Language.objects.filter(code=SOLUTION_LANGUAGE).first()
        if language is None:
            raise CommandError(f"til topilmadi: {SOLUTION_LANGUAGE}")
        self.language: Language = language
        self.topics = {topic.slug: topic for topic in Topic.objects.all()}

        tasks: list[dict[str, Any]] = manifest["tasks"]
        wanted = {code.strip() for code in options["codes"].split(",") if code.strip()}
        sizes = {
            task["code"]: abramyan.solution_size(self._solution(task["code"])) for task in tasks
        }
        estimates = abramyan.estimate(tasks, sizes)

        problems: dict[str, Problem] = {}
        for task in tasks:
            if wanted and task["code"] not in wanted:
                continue
            problems[task["code"]] = self._problem(task, estimates[task["code"]].difficulty)
        self._plan(manifest["study_plan"], problems)
        self.stdout.write(self.style.SUCCESS(f"{len(problems)} masala import qilindi"))

    # ── one problem ───────────────────────────────────────────────────
    def _solution(self, code: str) -> str:
        path = self.root / "solutions" / f"{code}.py"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def _texts(self, task: dict[str, Any], lang: str) -> dict[str, str]:
        statement = task["statement_html"][lang]
        out = {"title": abramyan.code_title(task["title"][lang])}
        for source, field in FIELDS.items():
            out[field] = abramyan.to_markdown(statement.get(source))
        if task["needs_file_io_rework"]:
            out["statement"] = abramyan.to_file_io(out["statement"], lang)
        if self.images:
            for field in FIELDS.values():
                out[field] = self._mirror(out[field])
        return out

    def _mirror(self, text: str) -> str:
        """Keep a statement's picture in our own storage: a link to another
        site would break the day that site moves it."""
        from problems.management.commands.mirror_assets import LOCAL_PREFIX, _fetch, _key_for

        def local(match: re.Match[str]) -> str:
            url = match.group(1)
            body, content_type = _fetch(url)
            key = _key_for(url, body, content_type)
            if self.storage and not storage.media_exists(storage.MEDIA_PREFIX + key):
                storage.put_media(storage.MEDIA_PREFIX + key, body, content_type)
            return match.group(0).replace(url, LOCAL_PREFIX + key)

        return _IMAGE.sub(local, text)

    @transaction.atomic
    def _problem(self, task: dict[str, Any], difficulty: int) -> Problem:
        base = self._texts(task, abramyan.BASE)
        real = task["checker"].startswith("real")
        problem, created = Problem.objects.update_or_create(
            slug=abramyan.slug(task["code"]),
            defaults={
                "title": base["title"],
                "statement": base["statement"],
                "input_format": base["input_format"],
                "output_format": base["output_format"],
                "note": base["note"],
                "statement_locale": abramyan.LOCALES[abramyan.BASE],
                "difficulty": difficulty,
                "time_limit_ms": abramyan.TIME_LIMIT_MS,
                "memory_limit_kb": abramyan.MEMORY_LIMIT_KB,
                "checker_type": Problem.Checker.REAL if real else Problem.Checker.STANDARD,
                "real_tolerance": abramyan.REAL_TOLERANCE,
                "io_mode": Problem.IoMode.BOTH
                if task["needs_file_io_rework"]
                else Problem.IoMode.STDIO,
                "source": abramyan.SOURCE,
                "is_official": False,
            },
        )
        if created:
            # A draft until `publish_abramyan`; a re-run never unpublishes.
            Problem.objects.filter(pk=problem.pk).update(is_public=False)
        if self.author is not None:
            problem.authors.add(self.author)
        problem.topics.set(
            [self.topics[slug] for slug in abramyan.TOPICS[task["section"]] if slug in self.topics]
        )
        for lang, locale in abramyan.LOCALES.items():
            if lang == abramyan.BASE:
                continue
            texts = self._texts(task, lang)
            ProblemTranslation.objects.update_or_create(
                problem=problem, locale=locale, defaults=texts
            )
        self._tests(problem, task["code"])
        self._solutions(problem, task)
        return problem

    def _tests(self, problem: Problem, code: str) -> None:
        folder = self.root / "tests" / code
        inputs = sorted(folder.glob("*.in"))
        if not inputs:
            raise CommandError(f"{code}: testlar topilmadi ({folder})")
        for path in inputs:
            order = int(path.stem)
            answer = path.with_suffix(".out").read_text(encoding="utf-8")
            data = path.read_text(encoding="utf-8")
            key = f"tests/{problem.slug}/{order}"
            refs = {"input_ref": f"s3://pending/{key}.in", "output_ref": f"s3://pending/{key}.out"}
            if self.storage:
                refs = {
                    "input_ref": storage.put_test_data(f"{key}.in", data),
                    "output_ref": storage.put_test_data(f"{key}.out", answer),
                }
            # The package's two examples are its first two tests (measured:
            # 2 200 of 2 200), so they are the samples.
            sample = order <= 2
            TestCase.objects.update_or_create(
                problem=problem,
                order=order,
                defaults={
                    **refs,
                    "is_sample": sample,
                    "group": TestCase.Group.SAMPLE if sample else TestCase.Group.UNCLASSIFIED,
                },
            )
        problem.tests.filter(order__gt=len(inputs)).delete()

    def _solutions(self, problem: Problem, task: dict[str, Any]) -> None:
        source = self._solution(task["code"])
        if not source:
            return
        if task["needs_file_io_rework"]:
            source = abramyan.file_solution(source)
        ReferenceSolution.objects.update_or_create(
            problem=problem, defaults={"language": self.language, "source": source}
        )
        ProblemSolution.objects.update_or_create(
            problem=problem,
            role=SolutionRole.REFERENCE,
            defaults={"language": self.language, "source": source, "expected_verdict": "AC"},
        )

    # ── the study plan ────────────────────────────────────────────────
    def _plan(self, plan: dict[str, Any], problems: dict[str, Problem]) -> None:
        def text(value: Any) -> dict[str, str]:
            return value if isinstance(value, dict) else {abramyan.BASE: str(value or "")}

        def others(
            values: dict[str, str], extra: dict[str, str] | None = None
        ) -> dict[str, dict[str, str]]:
            return {
                abramyan.LOCALES[lang]: {
                    "title": values.get(lang, ""),
                    "description": (extra or {}).get(lang, ""),
                }
                for lang in abramyan.LOCALES
                if lang != abramyan.BASE and values.get(lang)
            }

        names = text(plan.get("name"))
        descriptions = {**text(plan.get("description")), **abramyan.PLAN_DESCRIPTION}
        sections = []
        for index, section in enumerate(plan["sections"], start=1):
            titles = section["title"]
            details = {
                lang: abramyan.plan_text(value)
                for lang, value in (section.get("description") or {}).items()
            }
            members = []
            for code in section["tasks"]:
                problem = (
                    problems.get(code) or Problem.objects.filter(slug=abramyan.slug(code)).first()
                )
                if problem is not None:
                    members.append(problem)
            sections.append(
                plans.Section(
                    order=index,
                    title=titles.get(abramyan.BASE, section["key"]),
                    description=details.get(abramyan.BASE, ""),
                    translations=others(titles, details),
                    problems=tuple(members),
                )
            )
        plans.upsert(
            slug=plan["slug"],
            title=names.get(abramyan.BASE, plan["slug"]),
            description=descriptions.get(abramyan.BASE, ""),
            locale=abramyan.BASE,
            translations=others(names, descriptions),
            sections=sections if problems else [],
        )
