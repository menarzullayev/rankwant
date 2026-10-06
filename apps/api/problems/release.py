"""Nashr darvozalari — release checklist (PROMPT_0 §6 · §9 · §10 · ADR 0052).

Checklist FAQAT hujjat emas: bu yerdagi har bir band kod darajasidagi gate.
Nashr rad etilganda javobda **barqaror kod** qaytadi, ya'ni mijoz uni
matn bo'yicha emas, kod bo'yicha taniydi (masalan «nima uchun nashr
qilib bo'lmaydi?» so'rovi aynan shu kodlarni chiqaradi).

Kodlar barqaror va o'zgarmas: ular API shartnomasining bir qismi.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from problems import testgroups
from problems.evaluation import EVALUATION_MODE_INVALID as EVALUATION_MODE_INVALID
from problems.evaluation import evaluation_error
from problems.models import (
    Problem,
    ProblemRevision,
    RevisionStatus,
    SolutionRole,
)

# ── Barqaror xato kodlari ─────────────────────────────────────────────

STATEMENT_INCOMPLETE = "STATEMENT_INCOMPLETE"
TEST_GROUP_MISSING = "TEST_GROUP_MISSING"
VALIDATOR_NOT_VERIFIED = "VALIDATOR_NOT_VERIFIED"
REFERENCE_FAILED = "REFERENCE_FAILED"
CHECKER_NOT_VERIFIED = "CHECKER_NOT_VERIFIED"
LIMITS_NOT_CALIBRATED = "LIMITS_NOT_CALIBRATED"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
REVISION_NOT_FROZEN = "REVISION_NOT_FROZEN"

#: Shartda bo'sh bo'lmasligi kerak bo'lgan maydonlar (PROMPT_0 §6).
REQUIRED_STATEMENT_FIELDS: tuple[str, ...] = ("title", "statement", "input_format", "output_format")

#: Etalon yechim tasdiqlangan deb hisoblanadigan holatlar (§4 · ADR 0049).
REFERENCE_READY = frozenset({Problem.Readiness.REF_SOLUTION_VERIFIED, Problem.Readiness.VALIDATED})


class Gate(NamedTuple):
    code: str
    passed: bool
    detail: str = ""


# ── §6 Statement to'liqligi ───────────────────────────────────────────


def missing_statement_fields(problem: Problem) -> list[str]:
    """Bo'sh, faqat probel yoki yo'q maydonlar (barqaror tartibda).

    `None` ham bo'sh: `TextField(blank=True)` da qiymat `""` bo'lishi
    mumkin, ya'ni faqat `is None` tekshirish yetarli emas.
    """
    missing = []
    for name in REQUIRED_STATEMENT_FIELDS:
        value = getattr(problem, name, None)
        if value is None or not str(value).strip():
            missing.append(name)
    return missing


def statement_gate(problem: Problem) -> Gate:
    missing = missing_statement_fields(problem)
    if missing:
        return Gate(STATEMENT_INCOMPLETE, False, f"missing: {', '.join(missing)}")
    if not problem.tests.filter(is_sample=True).exists():
        return Gate(STATEMENT_INCOMPLETE, False, "missing: sample test")
    return Gate(STATEMENT_INCOMPLETE, True)


# ── §3 Test guruhlari ─────────────────────────────────────────────────


def test_group_gate(problem: Problem) -> Gate:
    missing = testgroups.missing_required_groups(problem.tests.values_list("group", flat=True))
    if missing:
        return Gate(TEST_GROUP_MISSING, False, f"missing: {', '.join(missing)}")
    return Gate(TEST_GROUP_MISSING, True)


# ── §1/§9 Validator ───────────────────────────────────────────────────


def validator_gate(problem: Problem) -> Gate:
    """Validator siyosati — aniq, yashirin emas (PROMPT_0 §1.3).

    Qoida: **validator ommaviy masala uchun majburiy**, chunki ommaviy
    masala hack qilinishi mumkin va tekshirilmagan kiritma judge'ni
    to'xtatib qo'yishi mumkin (ADR-0020). Qoralama uchun ixtiyoriy —
    muallif statement yozayotganda to'sib qo'yilmasin.
    """
    if not problem.is_public:
        return Gate(VALIDATOR_NOT_VERIFIED, True, "optional for a draft")
    row = getattr(problem, "validator", None)
    if row is None:
        return Gate(VALIDATOR_NOT_VERIFIED, False, "no validator: required for a public problem")
    if row.verified_at is None:
        return Gate(VALIDATOR_NOT_VERIFIED, False, "declared but not verified")
    return Gate(VALIDATOR_NOT_VERIFIED, True)


# ── §4 Etalon yechim ──────────────────────────────────────────────────


def reference_gate(problem: Problem) -> Gate:
    if problem.readiness in REFERENCE_READY:
        return Gate(REFERENCE_FAILED, True)
    detail = f"readiness={problem.readiness}"
    solution = problem.solutions.filter(role=SolutionRole.REFERENCE).first()
    if solution is None:
        detail += "; no reference solution"
    return Gate(REFERENCE_FAILED, False, detail)


# ── §2 Checker ────────────────────────────────────────────────────────


def checker_gate(problem: Problem) -> Gate:
    """Buzuq checker eng yomon holat — u natijani har qanday holatda
    buzadi. Shu sababli tekshiruv `standard` uchun ham talab qilinadi."""
    if problem.checker_verified_at is None:
        return Gate(CHECKER_NOT_VERIFIED, False, f"type={problem.checker_type}")
    return Gate(CHECKER_NOT_VERIFIED, True)


def evaluation_gate(problem: Problem) -> Gate:
    """The `io_mode` / `checker_type` pair must be one the judge implements.

    A verified checker is not enough: `both` with a special checker hands
    that checker an empty answer whenever the solution writes `output.txt`.
    The rules and their proof are in `problems/evaluation.py`.
    """
    error = evaluation_error(problem)
    if error:
        return Gate(EVALUATION_MODE_INVALID, False, error)
    return Gate(EVALUATION_MODE_INVALID, True)


# ── §5 Limitlar ───────────────────────────────────────────────────────


def limits_gate(problem: Problem) -> Gate:
    """Kalibrlash dalili: `ProblemRevision` uchun o'lchov bo'lishi kerak.

    Revision yo'q bo'lsa ham shart — ya'ni «faqat maydon to'ldirilgan»
    yetarli emas, o'lchov qayerda olingani ham saqlanishi kerak.
    """
    revision = problem.current_revision
    if revision is None:
        return Gate(LIMITS_NOT_CALIBRATED, False, "no revision")
    if not revision.calibrations.exists():
        detail = f"revision r{revision.version} has no measurement"
        return Gate(LIMITS_NOT_CALIBRATED, False, detail)
    return Gate(LIMITS_NOT_CALIBRATED, True)


# ── §7 Review ─────────────────────────────────────────────────────────


def review_gate(problem: Problem) -> Gate:
    if problem.readiness == Problem.Readiness.VALIDATED:
        return Gate(REVIEW_REQUIRED, True)
    return Gate(REVIEW_REQUIRED, False, f"readiness={problem.readiness}")


# ── §10 Revision muzlatilgan ──────────────────────────────────────────


def revision_gate(problem: Problem) -> Gate:
    revision = problem.current_revision
    if revision is None:
        return Gate(REVISION_NOT_FROZEN, False, "no revision")
    if not revision.is_frozen:
        return Gate(REVISION_NOT_FROZEN, False, f"r{revision.version} is {revision.status}")
    return Gate(REVISION_NOT_FROZEN, True)


# ── To'liq hisobot ────────────────────────────────────────────────────

#: Tartib muhim: birinchi yiqilgan gate birinchi ko'rsatiladi.
GATES = (
    statement_gate,
    test_group_gate,
    validator_gate,
    reference_gate,
    checker_gate,
    evaluation_gate,
    limits_gate,
    review_gate,
    revision_gate,
)


def release_report(problem: Problem) -> list[Gate]:
    return [gate(problem) for gate in GATES]


def blocking_codes(problem: Problem) -> list[str]:
    return [gate.code for gate in release_report(problem) if not gate.passed]


def release_payload(problem: Problem) -> dict[str, Any]:
    """API javobi: har gate uchun holat, sabab va to'liq ro'yxat."""
    gates = release_report(problem)
    failed = [g for g in gates if not g.passed]
    return {
        "can_publish": not failed,
        "failed": [{"code": g.code, "detail": g.detail} for g in failed],
        "gates": [{"code": g.code, "passed": g.passed, "detail": g.detail} for g in gates],
    }


def assert_publishable(problem: Problem) -> None:
    """Nashr uchun yakuniy tekshiruv — barcha gate o'tishi shart."""
    from rest_framework.exceptions import ValidationError

    failed = [g for g in release_report(problem) if not g.passed]
    if failed:
        raise ValidationError({"is_public": [{"code": g.code, "detail": g.detail} for g in failed]})


def snapshot_package(problem: Problem) -> dict[str, Any]:
    """Paket surati — revision muzlatilganda yoziladi (§10).

    Test matni S3 da qoladi: bu yerda faqat havola. Ya'ni surat yengil va
    artefakt o'zgarmaydi — o'zgarsa `package_hash` bilan aniqlanadi.
    """
    tests = [
        {
            "order": t.order,
            "input_ref": t.input_ref,
            "output_ref": t.output_ref,
            "is_sample": t.is_sample,
            "group": t.group,
            "points": t.points,
        }
        for t in problem.tests.order_by("order")
    ]
    solutions = [
        {"role": s.role, "language": getattr(s.language, "code", ""), "source": s.source}
        for s in problem.solutions.order_by("role")
    ]
    return {
        "problem": problem.slug,
        "statement": {
            "title": problem.title,
            "statement": problem.statement,
            "input_format": problem.input_format,
            "output_format": problem.output_format,
            "note": problem.note,
            "editorial": problem.editorial,
            "locale": problem.statement_locale,
        },
        "limits": {
            "time_limit_ms": problem.time_limit_ms,
            "memory_limit_kb": problem.memory_limit_kb,
            "io_mode": problem.io_mode,
        },
        "judge": {
            "checker_type": problem.checker_type,
            "checker_source": problem.checker_source,
            "checker_language": getattr(problem.checker_language, "code", ""),
            "interactor_source": problem.interactor_source,
            "interactor_language": getattr(problem.interactor_language, "code", ""),
        },
        "validator": _validator_part(problem),
        "tests": tests,
        "solutions": solutions,
        "metadata": {
            "difficulty": problem.difficulty,
            "readiness": problem.readiness,
            "topics": sorted(problem.topics.values_list("slug", flat=True)),
        },
    }


def _validator_part(problem: Problem) -> dict[str, Any] | None:
    row = getattr(problem, "validator", None)
    if row is None:
        return None
    return {
        "language": getattr(row.language, "code", ""),
        "source": row.source,
        "verified_at": row.verified_at.isoformat() if row.verified_at else None,
    }


def package_hash(package: dict[str, Any]) -> str:
    """Paketning SHA-256 i — muzlatish paytida yoziladi.

    Kalit tartibi bo'yicha saralanadi: JSON lug'at tartibi Python'da
    kiritish tartibiga bog'liq, ya'ni kiritish tartibi o'zgarsa xesh ham
    o'zgarib, soxta mismatch chiqardi.
    """
    import hashlib
    import json

    blob = json.dumps(package, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def next_version(problem: Problem) -> int:
    """Yangi revision raqami — mavjudlarning maksimumi + 1.

    Poyga: ikki so'rov bir vaqtda kelsa ikkalasi ham bir xil raqam
    olishi mumkin. `uniq_revision_version` cheklovi buni ushlaydi va
    chaqiruvchi qayta urinadi (qabul qilinadigan: revision kamdan
    yaratiladi).
    """
    last = (
        ProblemRevision.objects.filter(problem=problem)
        .order_by("-version")
        .values_list("version", flat=True)
        .first()
    )
    return (last or 0) + 1


def create_revision(problem: Problem, *, actor: Any = None) -> ProblemRevision:
    """Joriy holatdan YANGI revision yaratadi (draft).

    ⚠️ Bu yagona yo'l: mavjud PUBLISHED revision o'zgarmaydi. Masala
    tahrirlansa — yangi revision, eskisi esa read-only qoladi.
    """
    package = snapshot_package(problem)
    return ProblemRevision.objects.create(
        problem=problem,
        version=next_version(problem),
        status=RevisionStatus.DRAFT,
        package=package,
        created_by=actor,
    )


def freeze_revision(revision: ProblemRevision) -> str:
    """Revisionni muzlatadi va paket xeshini yozadi.

    Muzlatilgandan keyin: testlar, statement, checker, validator, limitlar
    va editorial o'zboshimchalik bilan o'zgarmaydi. O'zgarish kerak bo'lsa
    — yangi revision (§10).
    """
    from django.utils import timezone

    if revision.is_frozen:
        return revision.package_hash

    revision.package = revision.package or snapshot_package(revision.problem)
    revision.package_hash = package_hash(revision.package)
    revision.status = RevisionStatus.FROZEN
    revision.frozen_at = revision.frozen_at or timezone.now()
    revision.save(update_fields=["package", "package_hash", "status", "frozen_at", "updated_at"])
    return revision.package_hash


def verify_package(revision: ProblemRevision) -> bool:
    """Paket o'zgarmaganmi — xesh bo'yicha (§8 · §10)."""
    if not revision.package_hash:
        return False
    return package_hash(revision.package) == revision.package_hash


def publish_revision(revision: ProblemRevision) -> None:
    """Revisionni nashr qiladi va masalaning ko'rsatkichini yangilaydi.

    Avval `assert_publishable` chaqirilishi shart — bu funksiya gate'
    larni qayta tekshirmaydi, u faqat o'tishni bajaradi. Ajratish ataylab:
    tekshiruv va o'tish ikki xil javobgarlik.
    """
    from django.db import transaction
    from django.utils import timezone

    with transaction.atomic():
        if not revision.is_frozen:
            raise RuntimeError(f"revision r{revision.version} is not frozen")
        problem = revision.problem
        previous = problem.current_revision
        revision.status = RevisionStatus.PUBLISHED
        revision.published_at = revision.published_at or timezone.now()
        revision.save(update_fields=["status", "published_at", "updated_at"])
        problem.current_revision = revision
        problem.save(update_fields=["current_revision", "updated_at"])
        if previous is not None and previous.pk != revision.pk:
            previous.status = RevisionStatus.DEPRECATED
            previous.save(update_fields=["status", "updated_at"])
