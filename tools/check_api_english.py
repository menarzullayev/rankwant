#!/usr/bin/env python3
"""API user-facing strings must be English.

Field names are already English snake_case. This check stops Uzbek (or
any non-English) *messages* from landing in exception constructors,
permission `.message`, and `{error:{message}}` / `{detail}` payloads.

There is no fallback locale: a missing UI translation shows the English
property name, so the API must not mix another language into the same
envelope.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "apps/api"
SKIP_PARTS = {
    "tests",
    "migrations",
    "management",
    ".venv",
    "site-packages",
    "__pycache__",
}

EXCEPTION_NAMES = {
    "ValidationError",
    "PermissionDenied",
    "AuthenticationFailed",
    "NotFound",
    "ParseError",
    "APIException",
    "Throttled",
    "HackError",
    "PrefsError",
    "PurchaseError",
    "TeamError",
    "TeamForbidden",
    "TurnstileError",
    "OAuthError",
    "ChangeError",
    "AvatarError",
    "ClassroomError",
    "ArenaError",
    "DuelError",
    "HackathonError",
    "SendError",
}

#: Distinctive Uzbek (or mixed) tokens that must not appear in API copy.
UZBEK = re.compile(
    r"(?i)\b("
    r"noto'?g'?ri|topilmadi|kutilgan|yetarli|majburiy|takror|"
    r"noma'?lum|foydalanuvchi|parol|musobaqa|yechim|masala|"
    r"jamoa|sinf|chaqiriq|raund|ruxsat|havola|kiriting|tanlanadi|"
    r"ishlat|ulangan|hisob|manzil|rasm|fayl|provayder|huquq|"
    r"guruh|amal|xato|xizmat|mavjud|kiritilgan|ma'?lumot|"
    r"bo'?lsin|bo'?lmasin|bo'?lmaydi|kerak|band|qabul|yopiq|"
    r"ochiq|tugagan|muddat|belgi|maydon|obyekt|ro'?yxat|"
    r"yeching|yechimingizni|egasisiz|tahlil|balans|"
    r"mukofoti|rejalash|ishtirok"
    r")\b"
)
UZBEK_APOS = re.compile(r"[ogʻqOGQ]['ʻ’]")
ALLOWED_NON_ASCII = set("–—…«»‘’“”±×÷")


def call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def is_english(text: str) -> bool:
    if UZBEK.search(text) or UZBEK_APOS.search(text):
        return False
    for ch in text:
        if ord(ch) > 127 and ch not in ALLOWED_NON_ASCII:
            return False
    return True


def collect_from_call(node: ast.Call) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            if child.value.strip() and not is_english(child.value):
                found.append((child.lineno, child.value))
    return found


def scan_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    problems: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and call_name(node) in EXCEPTION_NAMES:
            problems.extend(collect_from_call(node))
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"message", "ANSWERED_MSG"}:
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if not is_english(node.value.value):
                            problems.append((node.value.lineno, node.value.value))
                if isinstance(target, ast.Attribute) and target.attr == "message":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if not is_english(node.value.value):
                            problems.append((node.value.lineno, node.value.value))
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str) and node.value.value.strip():
                if not is_english(node.value.value):
                    problems.append((node.value.lineno, node.value.value))
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=False):
                if not isinstance(key, ast.Constant) or key.value not in {"message", "detail"}:
                    continue
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    if value.value.strip() and not is_english(value.value):
                        problems.append((value.lineno, value.value))
                if isinstance(value, ast.JoinedStr):
                    for part in value.values:
                        if isinstance(part, ast.Constant) and isinstance(part.value, str):
                            if part.value.strip() and not is_english(part.value):
                                problems.append((value.lineno, part.value))
    rel = path.relative_to(ROOT)
    return [f"{rel}:{line}: {text!r}" for line, text in problems]


def main() -> int:
    if not API.exists():
        sys.exit(f"API topilmadi: {API}")
    files = [
        p
        for p in API.rglob("*.py")
        if not any(part in SKIP_PARTS for part in p.parts)
    ]
    if not files:
        sys.exit(f"i18n: API manba fayllar topilmadi ({API})")
    problems: list[str] = []
    for path in files:
        problems.extend(scan_file(path))
    if problems:
        print("API messages must be English:")
        for row in problems[:40]:
            print(f"  {row}")
        if len(problems) > 40:
            print(f"  … and {len(problems) - 40} more")
        return 1
    print(f"API English: {len(files)} files — user-facing messages are English ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
