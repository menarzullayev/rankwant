#!/usr/bin/env python3
"""AI qatlami chegarasi — `apps/api/ai/` hech narsaga bog'lanmasin.

NEGA KERAK: D6 qarori AI Gateway'ni **monolit modul** qilib qo'ydi
(`apps/api/ai/`). Chegara shu: AI kodi Django DB modelini import
qilmaydi, testdata o'qimaydi va `DATABASE_URL` ni bilmaydi. Sabab —
AI qatlami keyin (Phase 3) ajratilishi mumkin; u bugun DB sxemasiga
yopishib qolsa, ajratish imkonsiz bo'ladi.

⚠️ Nega STATIK (AST), nafaqat runtime: bugun `apps/api/ai/` deyarli
bo'sh — import qilib tekshirish HECH NARSANI o'lchamaydi (vakuumli
yashil). Statik tekshiruv kelajakdagi kodni BUGUN taqiqlaydi.
Pretsedent: `services/judge-go/main.go:27-31` da `DATABASE_URL` uchun
aynan shunday guard bor.

Taqiqlangan (AST bo'yicha):
  * har qanday Django model importi — `from <app>.models import`,
    `from .models import`, `import <app>.models`;
  * `django.db` va `django.contrib.*` importlari;
  * `DATABASE_URL` satri (env o'qish ham — satr sifatida tutuladi);
  * testdata o'qish — `open(...)` / `Path(...)` / `*.read_*()` ichida
    `testdata`, `fixtures/` yoki `*.json`.

CHIQISH KODLARI:
  0 — chegara toza
  1 — chegara buzilgan (har biri `fayl:satr — sabab` ko'rinishida)
  2 — o'qib bo'lmadi (qamrov yo'q yoki fayl sintaksisi buzuq)

⚠️ 2 hech qachon «toza» deb o'qilmaydi: o'lchovsiz yashil — yolg'on
yashil.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _boundary_apps
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

#: Qamrov: faqat AI qatlami. Boshqa app'lar bu darvozaga kirmaydi.
SCOPE = ROOT / "apps/api/ai"

#: `from django.db import ...`, `from django.contrib.auth.models import ...`.
FORBIDDEN_DJANGO = ("django.db", "django.contrib")

#: Testdata yo'li belgilarи (kichik harfga keltirilib solishtiriladi).
DATASET_MARKERS = ("testdata", "test_data", "test-data", "fixtures/", "/fixtures")

#: Fayl o'qish metodlari — `Path(...).read_text()` kabi zanjir oxiri.
READ_METHODS = ("read_text", "read_bytes", "read_json", "read_csv", "readlines")

#: AI qatlami bu o'zgaruvchini bilmasligi shart.
DB_URL = "DATABASE_URL"

#: Skanerdan chiqariladigan papkalar (kesh, nusxa).
SKIP_PARTS = {"__pycache__"}


def _is_model_import(module: str | None) -> bool:
    """`models` yoki `<app>.models` — har qanday Django model moduli."""
    if not module:
        return False
    return module == "models" or module.endswith(".models")


def _imports_models(node: ast.ImportFrom) -> bool:
    """`from … import models` — import qilinayotgan nomlar orasida `models` bormi."""
    return any(alias.name == "models" for alias in node.names)


def _is_django_forbidden(module: str | None) -> bool:
    """`django.db*` yoki `django.contrib*` — DB/sxema qatlamiga tegish."""
    if not module:
        return False
    return (
        module == FORBIDDEN_DJANGO[0]
        or module.startswith(FORBIDDEN_DJANGO[0] + ".")
        or module == FORBIDDEN_DJANGO[1]
        or module.startswith(FORBIDDEN_DJANGO[1] + ".")
    )


def _looks_like_dataset(text: str) -> bool:
    """Satr testdata yo'liga o'xshaydimi (`testdata`, `fixtures/`, `*.json`)."""
    low = text.lower()
    if any(marker in low for marker in DATASET_MARKERS):
        return True
    return low.endswith(".json")


def _call_name(node: ast.Call) -> str:
    """Chaqiruv nomi: `open` → `open`, `Path(...).read_text()` → `read_text`."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _string_constants(node: ast.AST) -> list[str]:
    """Chaqiruv ichidagi barcha satr literallari (receiver ham kiradi)."""
    return [
        sub.value
        for sub in ast.walk(node)
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
    ]


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Docstring tugunlarining `id()` to'plami.

    ⚠️ Docstring — HUJJAT, kod emas. Chegarani hujjatlashtirgan satr
    (`DATABASE_URL` haqidagi izoh) buzilish bo'lib o'qilmasligi kerak;
    aks holda qoidani yozishning o'zi qoidani buzardi.
    """
    owners = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    ids: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, owners):
            continue
        body = getattr(node, "body", [])
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ids.add(id(body[0].value))
    return ids


def _scan_file(path: Path, apps: set[str]) -> list[str]:
    """Bitta fayl bo'yicha buzilishlar ro'yxati (`fayl:satr — sabab`)."""
    rel = path.relative_to(ROOT).as_posix()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"{rel}: o'qib bo'lmadi — {exc}") from exc

    docstrings = _docstring_nodes(tree)
    problems: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if _is_model_import(node.module):
                problems.append(
                    f"{rel}:{node.lineno} — Django model importi ({node.module or '.'})"
                )
            elif node.module in apps and _imports_models(node):
                # `from <app> import models` — modul app nomi, nom `models`.
                problems.append(
                    f"{rel}:{node.lineno} — Django model importi "
                    f"(from {node.module} import models)"
                )
            elif node.level >= 1 and not node.module and _imports_models(node):
                # `from . import models` — nisbiy, modul yo'q, nom `models`.
                problems.append(
                    f"{rel}:{node.lineno} — Django model importi (from . import models)"
                )
            if _is_django_forbidden(node.module):
                problems.append(f"{rel}:{node.lineno} — Django importi ({node.module})")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if _is_model_import(alias.name):
                    problems.append(
                        f"{rel}:{node.lineno} — Django model importi ({alias.name})"
                    )
                if _is_django_forbidden(alias.name):
                    problems.append(f"{rel}:{node.lineno} — Django importi ({alias.name})")

        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
            and DB_URL in node.value
        ):
            problems.append(f"{rel}:{node.lineno} — `{DB_URL}` satri")

        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name in {"open", "Path"} or name in READ_METHODS:
                for value in _string_constants(node):
                    if _looks_like_dataset(value):
                        problems.append(
                            f"{rel}:{node.lineno} — testdata o'qish ({value!r})"
                        )
                        break
    return problems


def main() -> int:
    if not SCOPE.is_dir():
        print(f"  ✗ qamrov topilmadi: {SCOPE.relative_to(ROOT).as_posix()} — o'lchov yo'q")
        return 2

    files = sorted(
        p for p in SCOPE.rglob("*.py") if not any(part in SKIP_PARTS for part in p.parts)
    )
    # `from <app> import models` ni tutish uchun app nomlari kerak.
    apps = _boundary_apps.apps()
    problems: list[str] = []
    try:
        for path in files:
            problems += _scan_file(path, apps)
    except ValueError as exc:
        print(f"  ✗ {exc}")
        return 2

    print(f"Tekshirildi: apps/api/ai — {len(files)} fayl")
    if problems:
        print(f"\n{len(problems)} ta chegara buzilishi:\n")
        for problem in problems:
            print(f"  {problem}")
        print("\nAI qatlami DB modeliga, testdata'ga yoki DATABASE_URL ga tegmasin.")
        return 1
    print("AI qatlami chegarasi toza ✓ (DB modeli · testdata · DATABASE_URL — yo'q)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
