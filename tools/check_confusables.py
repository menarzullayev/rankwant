#!/usr/bin/env python3
"""Kod identifikatorlarida chalkashtirib bo'ladigan harflarni topadi.

Nega kerak: 2026-09-18 da `tests/test_warn_email_quota.py` ichida
`test_bir_kunda_ikki_marta_yurса_ham_bitta_yozuv` topildi — undagi `са`
**kirill** edi, lotin `sa` esa ko'rinishi bilan bir xil. Ya'ni:

  * test nomini qidirib topib bo'lmasdi (klaviaturadan `yursa` yozgan
    odam topa olmaydi);
  * pytest chiqishida u lotinchaga o'xshab ko'rinadi, ya'ni xato
    ko'rinmaydi;
  * `git grep`, IDE «Find usages», refactor vositalari — hammasi uni
    boshqa nom deb biladi.

Xato men tomonimdan yozilgan edi va ikki marta ko'rildi, tuzatilmadi:
birinchi tuzatish faqat faylning BOSHIDAGI nusxani o'zgartirgan, pytest
ko'rsatadigan nom esa o'sha holicha qolgan. Shuning uchun qo'lda emas,
tekshiruv bilan ushlanadi.

Qamrov ataylab TOR: faqat `def`, `class` va import qilinadigan nomlar.
Matn ichidagi kirill (tarjimalar, izohlar, hujjatlar) — butunlay normal
va bu tekshiruv ularga TEGMAYDI.

Ishlatish:
    python tools/check_confusables.py
"""

from __future__ import annotations

import ast
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Kod yoziladigan joylar. Hujjat (`docs/`) ataylab yo'q — u kirill
#: matnni o'z ichiga oladi va bu yerda qidirilmaydi.
ROOTS = ["apps/api", "apps/web/src", "tools", ".githooks", "services"]
SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".sh", ".yml", ".yaml"}

#: Kirill bloklari — `str.isascii()` yetarli emas: kirill ham, lotin ham
#: ASCII EMAS, ya'ni kirillni lotindan blok bo'yicha ajratish kerak.
CONFUSABLE_BLOCKS = (
    ("CYRILLIC", "kirill"),
    ("GREEK", "grek"),
)


def script_of(char: str) -> str | None:
    """Belgining yozuvini qaytaradi — `CYRILLIC`, `GREEK` yoki `None`."""
    try:
        name = unicodedata.name(char)
    except ValueError:
        return None
    for prefix, label in CONFUSABLE_BLOCKS:
        if name.startswith(prefix):
            return label
    return None


def scan_text(path: Path, text: str) -> list[str]:
    """Bitta fayldagi shubhali identifikatorlar."""
    found: list[str] = []

    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            return [f"{path}: o'qib bo'lmadi (sintaksis): {exc}"]
        names: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append((node.name, node.lineno))
            elif isinstance(node, ast.Name):
                names.append((node.id, node.lineno))
            elif isinstance(node, ast.arg):
                names.append((node.arg, node.lineno))
    else:
        # Python bo'lmagan fayllar: faqat e'lon qilinayotgan NOMNI olamiz,
        # butun qatorni emas. Butun qator olinsa, qiymat ichidagi matn ham
        # tekshiriladi va u yerda grek harf normal bo'ladi — o'lchandi
        # (2026-09-18): `const FORMULA_SKILLS = "Skills = Σ pᵢ × …"` yolg'on
        # xato berdi. Matematik belgi — matn, identifikator emas.
        names = []
        for n, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            match = re.match(
                r"(?:export\s+)?(?:async\s+)?(?:def|class|function|const|let|var)\s+([^\s(=:;]+)",
                stripped,
            )
            if match:
                names.append((match.group(1), n))

    for name, lineno in names:
        bad = {script_of(c) for c in name if not c.isascii()}
        bad.discard(None)
        if bad:
            where = f"{path.relative_to(ROOT)}:{lineno}"
            found.append(f"{where}: `{name}` ichida {', '.join(sorted(bad))} harf")
    return found


def main() -> int:
    failures: list[str] = []
    checked = 0

    for root_name in ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            if any(part in {"node_modules", ".next", "__pycache__", ".venv"} for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            checked += 1
            failures += scan_text(path, text)

    if failures:
        print(f"Chalkashtirib bo'ladigan harflar ({len(failures)} ta):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nTuzatish: kirill/grek harfni lotin ekvivalentiga almashtiring "
            "(ko'rinishi bir xil, lekin boshqa belgi).",
            file=sys.stderr,
        )
        return 1

    print(f"Identifikatorlar: {checked} ta fayl tekshirildi, chalkash harf yo'q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
