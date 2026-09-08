"""KEP.uz arxivini import qilish.

Ishlatish:
    python manage.py import_kep --limit 50        # sinov uchun
    python manage.py import_kep                   # butun arxiv
    python manage.py import_kep --ids 1,120,2348  # aniq masalalar

Masalalar QORALAMA bo'lib tushadi. Ochiq API yashirin testlarni
bermaydi, ya'ni yechimni tekshirib bo'lmaydi; ommaga chiqarish uchun
`--publish` ni ATAYLAB berish kerak (masalan, UI ni sinash uchun).
"""

from __future__ import annotations

import time
from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from core.models import User
from problems import kep, storage
from problems.models import (
    Language,
    Problem,
    ProblemLanguage,
    SimilarProblem,
    TestCase,
    Topic,
    Validator,
)


class Command(BaseCommand):
    help = "KEP.uz arxividan masalalarni import qiladi (standart holda qoralama)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=0, help="0 — butun arxiv")
        parser.add_argument("--ids", default="", help="Vergul bilan ajratilgan KEP raqamlari")
        parser.add_argument("--sleep", type=float, default=0.2, help="So'rovlar orasidagi tanaffus")
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Avval import qilinganlarini ham qayta yozadi",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Ommaga chiqaradi. Testlar yo'q — faqat sinov uchun.",
        )
        parser.add_argument("--no-samples", action="store_true", help="S3 ga tegmaydi")

    def handle(self, *args: Any, **options: Any) -> None:
        self.sleep: float = options["sleep"]
        self.publish: bool = options["publish"]
        self.with_samples: bool = not options["no_samples"]

        self.topics: dict[tuple[str, int], Topic] = {}
        self.authors: dict[str, User | None] = {}
        self.languages = {lang.code: lang for lang in Language.objects.all()}
        self.taken_slugs = set(Problem.objects.values_list("slug", flat=True))
        #: KEP raqami → bizdagi masala. O'xshashlik grafi uchun kerak,
        #: chunki A→B havolasi B import qilinmaguncha yasalmaydi.
        self.imported: dict[int, Problem] = {}
        self.similar: dict[int, list[tuple[int, float]]] = {}
        self.attachment_warnings = 0

        if self.with_samples:
            storage.ensure_bucket()

        self.sync_tags()

        for index, kep_id in enumerate(self.target_ids(options), start=1):
            try:
                payload = kep.problem(kep_id)
            except Exception as error:  # tarmoq yoki o'chirilgan masala
                self.stderr.write(f"#{kep_id} olinmadi: {error}")
                continue
            if not options["refresh"] and self.existing(kep_id):
                continue
            self.import_problem(payload)
            if index % 25 == 0:
                self.stdout.write(f"  … {index} ta ko'rildi, {len(self.imported)} import qilindi")
            time.sleep(self.sleep)

        links = self.link_similar()
        note = "ommaviy" if self.publish else "qoralama"
        self.stdout.write(
            self.style.SUCCESS(
                f"{len(self.imported)} masala import qilindi ({note}), "
                f"{Topic.objects.count()} mavzu, {links} o'xshashlik havolasi"
            )
        )
        if self.attachment_warnings:
            self.stdout.write(
                f"DIQQAT: {self.attachment_warnings} masalada biriktirma bor — "
                "ular hali ko'chirilmaydi"
            )

    # ── manba ro'yxati ──────────────────────────────────────────────
    def target_ids(self, options: dict[str, Any]) -> list[int]:
        if options["ids"]:
            try:
                return [int(part) for part in options["ids"].split(",") if part.strip()]
            except ValueError as error:
                raise CommandError(f"--ids noto'g'ri: {error}") from error

        ids = [row["id"] for row in kep.iter_summaries()]
        ids.reverse()  # eskisidan yangisiga — raqamlar tabiiy tartibda bersin
        limit: int = options["limit"]
        return ids[-limit:] if limit else ids

    def existing(self, kep_id: int) -> Problem | None:
        return Problem.objects.filter(source_url=f"{kep.SITE}/problems/{kep_id}").first()

    # ── teglar ──────────────────────────────────────────────────────
    def sync_tags(self) -> None:
        for row in kep.tags():
            self.ensure_topic("tag", row["id"], row["name"])
        self.stdout.write(f"{Topic.objects.count()} teg tayyor")

    def ensure_topic(self, kind: str, kep_id: int, name: str) -> Topic:
        cached = self.topics.get((kind, kep_id))
        if cached is not None:
            return cached
        # Bir xil nomli ikki teg bitta mavzuga qo'shiladi — bu ataylab:
        # arxivda «Satrlar» ikki marta bo'lsa ham foydalanuvchi uchun u
        # bitta filtr bo'lishi kerak.
        slug = slugify(name)[:50].strip("-") or f"mavzu-{kep_id}"
        topic, _ = Topic.objects.get_or_create(slug=slug, defaults={"name_uz": name})
        self.topics[(kind, kep_id)] = topic
        return topic

    # ── bitta masala ────────────────────────────────────────────────
    @transaction.atomic
    def import_problem(self, payload: dict[str, Any]) -> None:
        kep_id = int(payload["id"])
        fields = kep.to_fields(payload)
        fields["author"] = self.author(payload.get("authorUsername"))
        fields["is_public"] = self.publish

        problem = self.existing(kep_id)
        if problem is None:
            fields["slug"] = kep.make_slug(fields["title"], kep_id, self.taken_slugs)
            problem = Problem.objects.create(**fields)
        else:
            for key, value in fields.items():
                setattr(problem, key, value)
            problem.save()

        self.apply_topics(problem, payload)
        self.apply_languages(problem, payload)
        if self.with_samples:
            self.apply_samples(problem, payload)
        self.apply_validator(problem, payload)

        if payload.get("attachments"):
            self.attachment_warnings += 1

        self.imported[kep_id] = problem
        self.similar[kep_id] = [
            (int(row["id"]), float(row.get("score") or 0))
            for row in payload.get("similarProblems") or []
        ]

    def apply_topics(self, problem: Problem, payload: dict[str, Any]) -> None:
        parents = [self.ensure_topic("topic", row["id"], row["name"]) for row in payload["topics"]]
        children = [self.ensure_topic("tag", row["id"], row["name"]) for row in payload["tags"]]
        # Ikki qatlam: KEP `topics` — yirik yo'nalish (Coding, SQL),
        # `tags` — uning ichidagi mavzu. Bir teg turli masalada turli
        # yo'nalish bilan uchraydi, shuning uchun BIRINCHI ko'rilgani
        # ota qilib olinadi va keyin o'zgartirilmaydi.
        if parents:
            for child in children:
                if child.parent_id is None and child.pk != parents[0].pk:
                    child.parent = parents[0]
                    child.save(update_fields=["parent"])
        problem.topics.set(parents + children)

    def apply_languages(self, problem: Problem, payload: dict[str, Any]) -> None:
        memory_mb = payload.get("memoryLimit") or 256
        allowed = []
        for entry in payload.get("availableLanguages") or []:
            language = self.languages.get(kep.LANGUAGES.get(entry.get("lang", ""), ""))
            if language is None:
                continue
            allowed.append(language.pk)
            ProblemLanguage.objects.update_or_create(
                problem=problem,
                language=language,
                defaults=kep.language_limits(entry, memory_mb),
            )
        problem.languages.exclude(language_id__in=allowed).delete()

    def apply_samples(self, problem: Problem, payload: dict[str, Any]) -> None:
        samples = payload.get("sampleTests") or []
        for order, sample in enumerate(samples, start=1):
            TestCase.objects.update_or_create(
                problem=problem,
                order=order,
                defaults={
                    "input_ref": storage.put_test_data(
                        f"tests/{problem.slug}/{order}.in", sample.get("input") or ""
                    ),
                    "output_ref": storage.put_test_data(
                        f"tests/{problem.slug}/{order}.out", sample.get("output") or ""
                    ),
                    "is_sample": True,
                },
            )
        problem.tests.filter(order__gt=len(samples)).delete()

    def apply_validator(self, problem: Problem, payload: dict[str, Any]) -> None:
        """Kirish validatori — hacking uchun kerak bo'ladi (ADR muhokamasi).

        Ochiq API uni deyarli har doim `null` qaytaradi; kelgan taqdirda
        yo'qotib qo'ymaymiz.
        """
        source = payload.get("checkInputSource")
        language = self.languages.get("cpp23")
        if not source or language is None:
            return
        Validator.objects.update_or_create(
            problem=problem, defaults={"language": language, "source": source}
        )

    # ── muallif ─────────────────────────────────────────────────────
    def author(self, username: str | None) -> User | None:
        """KEP mualliflari uchun soya hisob.

        `kep-` prefiksi ataylab: bizdagi `admin` KEP dagi `admin` emas,
        prefikssiz 1900 ta masala noto'g'ri odamga yozilib qolardi.
        Hisob NOFAOL va parolsiz — kirish uchun emas, atribut uchun.
        Muallifning o'zi ro'yxatdan o'tsa, keyin biriktirib qo'yiladi.
        """
        if not username:
            return None
        if username in self.authors:
            return self.authors[username]

        user = User.objects.filter(username=f"kep-{username}"[:150]).first()
        if user is None:
            try:
                profile = kep.user(username)
            except Exception:
                profile = {}
            display = " ".join(
                part for part in (profile.get("firstName"), profile.get("lastName")) if part
            )
            user = User(
                username=f"kep-{username}"[:150],
                display_name=display or username,
                avatar_url=profile.get("avatar") or "",
                is_active=False,
            )
            user.set_unusable_password()
            user.save()
        self.authors[username] = user
        return user

    # ── o'xshashlik grafi ───────────────────────────────────────────
    def link_similar(self) -> int:
        rows = []
        for kep_id, targets in self.similar.items():
            problem = self.imported.get(kep_id)
            if problem is None:
                continue
            for target_id, score in targets:
                similar = self.imported.get(target_id) or self.existing(target_id)
                if similar is None or similar.pk == problem.pk:
                    continue
                rows.append(
                    SimilarProblem(problem=problem, similar=similar, score=score, source="kep.uz")
                )
        SimilarProblem.objects.bulk_create(rows, ignore_conflicts=True)
        return len(rows)
